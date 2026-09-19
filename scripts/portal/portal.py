import math
from engine.components.component import Component
from engine.components.box_collider2d import BoxCollider2D
from engine.components.rigidbody2d import Rigidbody2D
from engine.utils.vector2 import Vector2


class Portal(Component):
    def __init__(self, target_portal=None, direction="UP", cooldown=0.5, damping=0.8):
        super().__init__()
        self.target_portal = target_portal
        self.direction = direction
        self.cooldown = cooldown
        self.damping = damping

        self.trigger = None
        self._cooldown_timer = 0.0

    def start(self):
        box_colliders = self.game_object.get_components(BoxCollider2D)

        for collider in box_colliders:
            if collider.is_trigger:
                self.trigger = collider
                break

        if self.trigger and self._on_enter not in self.trigger.on_trigger_enter:
            self.trigger.on_trigger_enter.append(self._on_enter)

    def update(self, delta_time):
        if self._cooldown_timer > 0:
            self._cooldown_timer -= delta_time

    def trigger_cooldown(self, time_val=None):
        self._cooldown_timer = time_val if time_val is not None else self.cooldown

    def _teleport(self, obj):
        if not self.target_portal:
            return

        target_script = self.target_portal.get_component(Portal)
        if not target_script:
            return

        target_position = Vector2(self.target_portal.transform.position.x, self.target_portal.transform.position.y)

        out_dir = target_script.direction

        if out_dir == "UP":
            target_position += Vector2(0, -189)
        elif out_dir == "DOWN":
            target_position += Vector2(0, 189)
        elif out_dir == "RIGHT":
            target_position += Vector2(152, 0)
        elif out_dir == "LEFT":
            target_position += Vector2(-152, 0)

        obj.transform.position.x = target_position.x
        obj.transform.position.y = target_position.y

        rb = obj.get_component(Rigidbody2D)
        if rb:
            if hasattr(rb, "position"):
                rb.position = Vector2(target_position.x, target_position.y)

            current_speed = math.hypot(rb.velocity.x, rb.velocity.y)
            out_speed = current_speed * target_script.damping

            if out_dir == "UP":
                rb.velocity = Vector2(0, -out_speed)
            elif out_dir == "DOWN":
                rb.velocity = Vector2(0, out_speed)
            elif out_dir == "RIGHT":
                rb.velocity = Vector2(out_speed, 0)
            elif out_dir == "LEFT":
                rb.velocity = Vector2(-out_speed, 0)

        max_cd = max(self.cooldown, target_script.cooldown)
        self.trigger_cooldown(max_cd)
        target_script.trigger_cooldown(max_cd)

    def _on_enter(self, trigger, other):
        if self._cooldown_timer > 0:
            return

        obj = other.game_object

        if obj.get_component(Rigidbody2D):
            self._teleport(obj)