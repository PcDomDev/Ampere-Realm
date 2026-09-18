import pygame.image
from engine.core.game_object import GameObject
from engine.core.scene import Scene
from engine.components.camera import Camera
from engine.components.rigidbody2d import Rigidbody2D
from engine.components.animator import Animator
from engine.components.sprite_renderer import SpriteRenderer
from engine.components.box_collider2d import BoxCollider2D
from engine.components.player_controller import PlayerController
from engine.utils.spritesheet_loader import load_spritesheet_animations

def build_platformer_scene():
    scene = Scene("Player")

    player = GameObject(
        x=0, y=-200,
        name="Player"
    )

    player.add_component(SpriteRenderer(
        z_index=2,
        anchor="center"
    ))

    player.add_component(BoxCollider2D(
        size=(80, 160),
        offset_x=0, offset_y=12,
        anchor="center"
    ))

    player.add_component(Rigidbody2D(
        gravity=2000,
        use_gravity=True,
        drag=2.0
    ))

    animations = load_spritesheet_animations("assets/player/player.json", "assets/player/player.png")

    player.add_component(Animator(
        animations=animations,
        default_animation="idle",
        frame_duration=0.035
    ))

    player.add_component(PlayerController(
        speed=500,
        jump_force=800,
        movement_type="platformer",
        max_jumps=2,
        anim_map = {
            "idle_right": "idle",
            "idle_left": "_idle",
            "walk_right": "walk",
            "walk_left": "_walk",
            "jump_right": "jump",
            "jump_left": "_jump"
        }
    ))

    scene.add_game_object(player)


    for index in range(50):
        scene.add_game_object(create_new_block(index, index*128, 128))

    camera_go = GameObject(name="Main Camera")
    camera = camera_go.add_component(Camera(
        target=player,
        follow_speed=6.0,
        smooth_follow=True
    ))
    scene.add_game_object(camera_go)
    scene.set_active_camera(camera)

    return scene

def create_new_block(number, x, y, image_path="assets/items/blocks/block.png"):
    block = GameObject(x, y, f"Block{number}")
    block.add_component(SpriteRenderer(pygame.image.load(image_path), anchor="center"))
    block.add_component(BoxCollider2D(size=(128, 128), offset_x=-12, offset_y=12, anchor="center"))

    return block

