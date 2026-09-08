from engine.components.box_collider2d import BoxCollider2D
from engine.components.sprite_renderer import SpriteRenderer
from engine.ui.ui_element import UIElement
from engine.utils.vector2 import Vector2


class Scene:
    """A collection of GameObjects, plus the logic to update, collide, and
    render them. This is engine machinery - what a scene *contains* (a
    controllable character, a platform, a menu, ...) belongs in
    scenes/game_scene.py or similar, not here.
    """

    def __init__(self, name="Scene"):
        self.name = name
        self.game_objects = []
        self.active_camera = None

    def add_game_object(self, game_object):
        game_object.scene = self
        self.game_objects.append(game_object)
        game_object.start()
        return game_object

    def remove_game_object(self, game_object):
        if game_object in self.game_objects:
            self.game_objects.remove(game_object)

    def find_game_object(self, name):
        """First GameObject with a matching `.name`, or None."""
        for go in self.game_objects:
            if go.name == name:
                return go
        return None

    def set_active_camera(self, camera):
        self.active_camera = camera

    def get_components(self, component_type):
        """Every component of `component_type` on every *active* GameObject.

        Uses GameObject.get_components (plural) rather than get_component
        (singular), so an object with more than one component of the same
        type (e.g. a compound collider) is fully represented rather than
        silently only contributing its first match.
        """
        components = []
        for go in self.game_objects:
            if go.active:
                components.extend(go.get_components(component_type))
        return components

    def start(self):
        for go in self.game_objects:
            go.start()

    def update(self, delta_time):
        for go in list(self.game_objects):
            if go.active:
                go.update(delta_time)

        self._process_triggers()

    def _process_triggers(self):
        colliders = self.get_components(BoxCollider2D)
        triggers = [c for c in colliders if c.is_trigger]

        for trigger in triggers:
            for other in colliders:
                if trigger is not other and other.game_object.active:
                    trigger.check_trigger_events(other)

    def render(self, screen):
        self._render_world(screen)
        self._render_ui(screen)

    def _render_world(self, screen):
        offset = Vector2(0.0, 0.0)
        if self.active_camera is not None:
            offset = self.active_camera.get_offset(screen.get_width(), screen.get_height())

        renderers = [r for r in self.get_components(SpriteRenderer) if r.enabled and r.sprite]
        renderers.sort(key=lambda r: (r.z_index, r.game_object.transform.position.y + r.offset_y))

        for r in renderers:
            transform = r.game_object.transform
            sprite = r.get_transformed_sprite(transform.rotation, transform.scale.x, transform.scale.y)
            if sprite is None:
                continue

            # Rotating/scaling changes the surface's own width/height, so
            # the draw position is recomputed to keep the sprite's *center*
            # fixed at the expected world position - the usual expected
            # pivot - rather than its top-left corner drifting as the
            # surface's bounding box changes size.
            original_w, original_h = r.sprite.get_size()
            center = Vector2(
                transform.position.x + original_w / 2.0,
                transform.position.y + original_h / 2.0,
            ) - offset

            new_w, new_h = sprite.get_size()
            draw_pos = Vector2(center.x - new_w / 2.0, center.y - new_h / 2.0)
            screen.blit(sprite, (round(draw_pos.x), round(draw_pos.y)))

    def _render_ui(self, screen):
        """UI draws last, directly in screen space - never offset by the
        camera, always on top of the world."""
        elements = [e for e in self.get_components(UIElement) if e.visible]
        elements.sort(key=lambda e: e.draw_order)
        for element in elements:
            element.draw(screen)
