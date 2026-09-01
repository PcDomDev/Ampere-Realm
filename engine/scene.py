from engine.components.box_collider2d import BoxCollider2D
from engine.components.sprite_renderer import SpriteRenderer
from engine.utils.vector2 import Vector2


class Scene:
    """A collection of GameObjects, plus the logic to update, collide, and
    render them. This is engine machinery - what a scene *contains* (a
    player, a floor, a coin, ...) belongs in scenes/game_scene.py or
    similar, not here.
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
        offset = Vector2(0.0, 0.0)
        if self.active_camera is not None:
            offset = self.active_camera.get_offset(screen.get_width(), screen.get_height())

        renderers = [r for r in self.get_components(SpriteRenderer) if r.enabled and r.sprite]
        renderers.sort(key=lambda r: (r.z_index, r.game_object.transform.position.y + r.offset_y))

        for r in renderers:
            draw_pos = r.game_object.transform.position - offset
            screen.blit(r.sprite, (round(draw_pos.x), round(draw_pos.y)))
