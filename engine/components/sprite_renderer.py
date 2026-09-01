from engine.components.component import Component


class SpriteRenderer(Component):
    """Draws `sprite` at its GameObject's transform position every frame.

    `z_index` controls draw-order between layers (lower draws first / behind).
    Within the same z_index, Scene sorts by `transform.position.y + offset_y`
    so objects lower on screen draw in front - a common cheap approximation
    of depth for top-down/platformer sprites. `offset_y` only affects that
    sort key, not the actual draw position, so you can nudge an object's
    "feet" reference point for sorting purposes without moving its sprite.
    """

    def __init__(self, sprite=None, z_index=0, offset_y=0):
        super().__init__()
        self.sprite = sprite
        self.z_index = z_index
        self.offset_y = offset_y

    def set_sprite(self, sprite):
        self.sprite = sprite
