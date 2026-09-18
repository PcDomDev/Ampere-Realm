from engine.components.component import Component
from engine.components.box_collider2d import BoxCollider2D
from engine.utils.vector2 import Vector2


class Portal(Component):
    def __init__(self, target_portal=None, direction="UP", cooldown=0.5):
        super().__init__()
        self.target_portal = target_portal
        self.direction = direction
        self.cooldown = cooldown

        self.trigger = None
        self._cooldown_timer = 0.0

    def start(self):
        box_colliders = self.game_object.get_components(BoxCollider2D)

        for collider in box_colliders:
            if collider.is_trigger:
                self.trigger = collider
                break

        if self.trigger:
            self.trigger.on_trigger_enter.append(self._on_enter)

    def update(self, delta_time):
        if self._cooldown_timer > 0:
            self._cooldown_timer -= delta_time

    def trigger_cooldown(self):
        self._cooldown_timer = self.cooldown

    def _teleport(self, player):
        if not self.target_portal:
            return

        target_script = self.target_portal.get_component(Portal)
        target_position = Vector2(self.target_portal.transform.position.x, self.target_portal.transform.position.y)

        if target_script.direction == "UP":
            target_position += Vector2(0, -189)
        elif target_script.direction == "DOWN":
            target_position += Vector2(0, 189)
        elif target_script.direction == "RIGHT":
            target_position += Vector2(152, 0)
        elif target_script.direction == "LEFT":
            target_position += Vector2(-152, 0)

        player.transform.position.x = target_position.x
        player.transform.position.y = target_position.y

        self.trigger_cooldown()
        target_script.trigger_cooldown()

    def _on_enter(self, trigger, other):
        if self._cooldown_timer > 0:
            return

        entering_object = other.game_object

        if entering_object.name == "Player":
            self._teleport(entering_object)