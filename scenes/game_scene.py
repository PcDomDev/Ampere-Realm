import json
import pygame

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

    animations = load_spritesheet_animations("assets/player/player.json", "assets/player/player.png")

    player = GameObject(x=100, y=100, name="Player")
    player.add_component(SpriteRenderer(z_index=1))
    player.add_component(Rigidbody2D(gravity=900, use_gravity=True, drag=3.0))
    player.add_component(BoxCollider2D(size=(90, 110), anchor="midbottom"))

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
            "run": "walk",
            "jump": "jump",
            "fall": "jump"
        }
    ))

    scene.add_game_object(player)

    ground = create_rectangle(
        x=-500, y=500,
        width=2000, height=100,
        color=(80, 80, 80),
        add_collider=True,
        add_rigidbody=False
    )
    scene.add_game_object(ground)

    scene.add_game_object(player)
    camera_go = GameObject(name="Main Camera")
    camera_comp = camera_go.add_component(Camera(target=player, follow_speed=6.0, smooth_follow=True))
    scene.add_game_object(camera_go)
    scene.set_active_camera(camera_comp)

    return scene