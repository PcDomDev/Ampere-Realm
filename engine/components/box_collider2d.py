import warnings

import pygame

from engine.components.component import Component
from engine.components.sprite_renderer import SpriteRenderer
from engine.utils.warnings import EngineWarning

# Every anchor name pygame.Rect actually understands. Anything else used to
# silently fall back to "topleft" with zero feedback - that's how a typo
# like anchor="buttom" went unnoticed (see docs/CHANGELOG.md).
_VALID_ANCHORS = {
    "topleft", "midtop", "topright",
    "midleft", "center", "midright",
    "bottomleft", "midbottom", "bottomright",
}


class BoxCollider2D(Component):
    """An axis-aligned box used for collision (solid) or overlap (trigger)
    detection.

    Sizing: pass `size=(w, h)` explicitly when you can - it's the most
    predictable option. If you omit it, the size is captured *once*, from
    whatever sprite is on this GameObject's SpriteRenderer at `start()`
    time, and then locked in place. It deliberately does **not** keep
    re-measuring the live sprite every frame, because this GameObject's
    sprite can change out from under it (an Animator swapping frames), and
    if two animation frames aren't pixel-identical in size, a collider that
    tracks the current frame changes shape mid-collision - which is exactly
    what produced the reported landing jitter (see docs/CHANGELOG.md for the
    full trace). If you deliberately want the hitbox to resize later (e.g. a
    crouch), call `set_size()` explicitly.
    """

    update_order = -90  # sync right after Rigidbody2D resolves movement

    def __init__(self, size=None, offset_x=0, offset_y=0, anchor="topleft", is_trigger=False):
        super().__init__()

        if anchor not in _VALID_ANCHORS:
            warnings.warn(
                f"BoxCollider2D: unknown anchor '{anchor}', falling back to 'topleft'. "
                f"Valid anchors are: {sorted(_VALID_ANCHORS)}",
                EngineWarning,
                stacklevel=2,
            )
            anchor = "topleft"

        self._explicit_size = tuple(size) if size is not None else None
        self._locked_size = self._explicit_size or (0, 0)

        self.offset_x = offset_x
        self.offset_y = offset_y
        self.anchor = anchor
        self.is_trigger = is_trigger

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.sprite_renderer = None

        self._overlapping_colliders = set()

        # Trigger callbacks: lists of `callback(trigger, other)`, not single
        # overridable methods. The original design (`self.on_trigger_enter =
        # a_function`, then internally calling `self.on_trigger_enter(self,
        # other)`) crashes with a TypeError the moment anyone *doesn't*
        # override it, because the un-overridden version is a bound method
        # and picks up an implicit extra `self`. Lists sidestep that
        # entirely, and let more than one listener subscribe.
        self.on_trigger_enter = []
        self.on_trigger_stay = []
        self.on_trigger_exit = []

    def start(self):
        self.sprite_renderer = self.game_object.get_component(SpriteRenderer)
        if self._explicit_size is None:
            self._locked_size = self._measure_from_sprite()
        self._update_rect()

    def _measure_from_sprite(self):
        if self.sprite_renderer and self.sprite_renderer.sprite:
            return self.sprite_renderer.sprite.get_size()
        return (0, 0)

    def set_size(self, width, height):
        """Explicitly (re)size the collider, e.g. for a deliberate crouch
        hitbox. Once called, the size is locked to (width, height) and will
        not be affected by sprite/animation changes."""
        self._explicit_size = (width, height)
        self._locked_size = (width, height)
        self._update_rect()

    def update(self, delta_time):
        self._update_rect()

    def _update_rect(self):
        w, h = self._locked_size
        self.rect = pygame.Rect(0, 0, w, h)

        transform = self.game_object.transform
        target_x = transform.position.x + self.offset_x
        target_y = transform.position.y + self.offset_y

        # anchor is validated in __init__, so this attribute always exists.
        # pygame quantizes this to an int rect internally (see
        # snap_*_to below for why that quantization must never leak into
        # collision *resolution*, only detection/rendering).
        setattr(self.rect, self.anchor, (target_x, target_y))

    # -- exact (unrounded) positioning, used for collision resolution ------------

    def _anchor_to_topleft_offset(self):
        """(dx, dy) such that top_left = anchor_point + (dx, dy), for this
        collider's current anchor and locked size.

        Computed via a throwaway rect at the origin. Since width/height are
        always integers, this is exact for the 4 corner/edge-midpoint
        anchors and correct to within pygame's own integer-division
        rounding for odd-sized "mid"/"center" anchors - the same precision
        pygame's anchors have everywhere else, no worse.
        """
        w, h = self._locked_size
        probe = pygame.Rect(0, 0, w, h)
        setattr(probe, self.anchor, (0, 0))
        return probe.left, probe.top

    def snap_left_to(self, world_x):
        """Move the owning Transform so this collider's left edge sits at
        exactly `world_x`, computed from the exact float transform position
        rather than the already pixel-rounded `.rect` - see
        Rigidbody2D._resolve_collisions_x for why."""
        dx, _ = self._anchor_to_topleft_offset()
        self.game_object.transform.position.x = world_x - dx - self.offset_x
        self._update_rect()

    def snap_right_to(self, world_x):
        dx, _ = self._anchor_to_topleft_offset()
        w, _ = self._locked_size
        self.game_object.transform.position.x = (world_x - w) - dx - self.offset_x
        self._update_rect()

    def snap_top_to(self, world_y):
        _, dy = self._anchor_to_topleft_offset()
        self.game_object.transform.position.y = world_y - dy - self.offset_y
        self._update_rect()

    def snap_bottom_to(self, world_y):
        _, dy = self._anchor_to_topleft_offset()
        _, h = self._locked_size
        self.game_object.transform.position.y = (world_y - h) - dy - self.offset_y
        self._update_rect()

    # -- triggers -----------------------------------------------------------------

    def check_trigger_events(self, other_collider):
        if not self.is_trigger or not isinstance(other_collider, BoxCollider2D):
            return

        is_touching = self.rect.colliderect(other_collider.rect)
        was_touching = other_collider in self._overlapping_colliders

        if is_touching and not was_touching:
            self._overlapping_colliders.add(other_collider)
            self._dispatch(self.on_trigger_enter, other_collider)
        elif is_touching and was_touching:
            self._dispatch(self.on_trigger_stay, other_collider)
        elif not is_touching and was_touching:
            self._overlapping_colliders.remove(other_collider)
            self._dispatch(self.on_trigger_exit, other_collider)

    def _dispatch(self, callbacks, other_collider):
        # Import here (not at module level) to avoid a circular import with
        # debug_manager, which itself imports BoxCollider2D for collider
        # visualization.
        from engine.debug_manager import DebugManager

        for callback in list(callbacks):  # copy: a callback may unsubscribe itself
            try:
                callback(self, other_collider)
            except Exception as exc:  # noqa: BLE001 - a bad user callback must not crash the game
                owner = getattr(self.game_object, "name", "?")
                DebugManager.log_error(f"Trigger callback on '{owner}' raised {exc!r}")
