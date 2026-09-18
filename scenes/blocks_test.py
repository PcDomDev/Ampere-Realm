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
from scripts.portal.portal import Portal

def build_test_scene():
    scene = Scene("Blocks Test")

    # Player
    player = create_player()
    scene.add_game_object(player)

    # Blocks
    for index in range(50):
        scene.add_game_object(create_default_block(index, index*128, 128))

    # Camera
    camera_go = GameObject(name="Main Camera")
    camera = camera_go.add_component(Camera(
        target=player,
        follow_speed=6.0,
        smooth_follow=True
    ))
    scene.add_game_object(camera_go)
    scene.set_active_camera(camera)

    return scene


def create_player( x=0, y=-200, name="Player", json_path="assets/player/player.json", png_path="assets/player/player.png", speed=500, jump_force=800, gravity=2000, anim_map=None):
    if anim_map is None:
        anim_map = {
            "idle_right": "idle",
            "idle_left": "_idle",
            "walk_right": "walk",
            "walk_left": "_walk",
            "jump_right": "jump",
            "jump_left": "_jump"
        }

    player = GameObject(
        x=x, y=y,
        name=name)

    player.add_component(SpriteRenderer(
        z_index=2,
        anchor="center"
    ))

    player.add_component(BoxCollider2D(
        size=(80, 160),
        offset_x=0,
        offset_y=12,
        anchor="center"
    ))

    player.add_component(Rigidbody2D(
        gravity=gravity,
        use_gravity=True,
        drag=2.0
    ))

    animations = load_spritesheet_animations(json_path, png_path)

    player.add_component(Animator(
        animations=animations,
        default_animation="idle",
        frame_duration=0.035
    ))

    player.add_component(PlayerController(
        speed=speed,
        jump_force=jump_force,
        movement_type="platformer",
        max_jumps=2,
        anim_map=anim_map
    ))

    return player


def create_default_block(number, x, y):
    block = GameObject(x=x, y=y, name=f"Block{number}")
    block.add_component(SpriteRenderer(sprite=pygame.image.load("assets/blocks/default/block.png"), anchor="center"))
    block.add_component(BoxCollider2D(size=(128, 128), offset_x=-12, offset_y=12, anchor="center"))
    return block


def create_portal_block(number, x, y, direction="UP", target_portal=None):
    portal = GameObject(x=x, y=y, name=f"Portal{number}")
    portal.add_component(SpriteRenderer(sprite=pygame.image.load(f"assets/blocks/portal/portal {direction.lower()}.png"), anchor="center"))
    portal.add_component(BoxCollider2D(size=(128, 128), offset_x=-12, offset_y=12, anchor="center"))

    dir_upper = direction.upper()
    if dir_upper == "UP":
        trigger_size = (128, 10)
        trigger_offset = (-12, -54)
    elif dir_upper == "DOWN":
        trigger_size = (128, 10)
        trigger_offset = (-12, 78)
    elif dir_upper == "LEFT":
        trigger_size = (10, 128)
        trigger_offset = (-78, 12)
    elif dir_upper == "RIGHT":
        trigger_size = (10, 128)
        trigger_offset = (54, 12)
    else:
        trigger_size = (128, 10)
        trigger_offset = (-12, -54)

    portal.add_component(BoxCollider2D(
        size=trigger_size,
        is_trigger=True,
        offset_x=trigger_offset[0],
        offset_y=trigger_offset[1],
        anchor="center"
    ))

    portal.add_component(Portal(target_portal=target_portal, direction=direction))

    if target_portal:
        first_portal_script = target_portal.get_component(Portal)
        if first_portal_script:
            first_portal_script.target_portal = portal

    return portal

