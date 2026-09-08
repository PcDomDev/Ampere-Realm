import json
import pygame

from engine.components import transform
from engine.scene import Scene
from engine.game_object import GameObject
from engine.primitives import create_rectangle
from engine.components.sprite_renderer import SpriteRenderer
from engine.components.rigidbody2d import Rigidbody2D
from engine.components.box_collider2d import BoxCollider2D
from engine.components.animator import Animator
from engine.components.player_controller import PlayerController
from engine.components.camera import Camera
from scripts.json_reader import load_spritesheet_animations

def build_game_scene():
    scene = Scene()

    animations = load_spritesheet_animations("assets/player/right/player.json", "assets/player/right/player.png")

    player = GameObject(x=0, y=-100, name="Player")
    player.add_component(SpriteRenderer(z_index=1))
    player.add_component(Rigidbody2D(
        gravity=900,
        use_gravity=True,
        drag=3.0))

    player.add_component(BoxCollider2D(
        size=(100, 150),
        offset_x=15,
        offset_y=38,
        anchor="topleft"
    ))

    player.add_component(Animator(
        animations=animations,
        default_animation="idle",
        frame_duration=0.08
    ))

    player.add_component(PlayerController(
        speed=250,
        jump_force=500,
        movement_type="platformer",
        max_jumps=2,
        anim_map={
            "idle": "idle",
            "walk_left": "walk",
            "walk_right": "walk",
            "jump": "jump"
        }
    ))

    scene.add_game_object(player)


    camera_go = GameObject(name="Main Camera")
    camera_comp = camera_go.add_component(Camera(
        target=player,
        follow_speed=6.0,
        smooth_follow=True
    ))

    scene.add_game_object(camera_go)
    scene.set_active_camera(camera_comp)

    scene.add_game_object(crete_box(9, 0, 0))
    scene.add_game_object(crete_box(10, 128, 0))
    scene.add_game_object(crete_box(11, 256, 0))


    return scene


def crete_box(number, x, y, z_index=0, sprite=pygame.image.load("assets/separately/Block.png"), size=(128, 128), offset_x=24, offset_y=48, anchor="topleft"):
    block = GameObject(x=x, y=y, name=str(number))
    block.add_component(SpriteRenderer(z_index=z_index, sprite=sprite))
    block.add_component(BoxCollider2D(
        size=size,
        offset_x=offset_x,
        offset_y=offset_y,
        anchor=anchor
    ))

    return block