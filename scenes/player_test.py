from engine.core.app import Engine
from engine.core.game_object import GameObject
from engine.core.scene import Scene
from engine.components.camera import Camera
from engine.components.rigidbody2d import Rigidbody2D
from engine.components.player_controller import PlayerController
from engine.primitives import create_square, create_rectangle


def build_platformer_scene():
    scene = Scene("Player")

    player = create_square(
        x=200, y=100,
        size=40,
        color=(60, 140, 230),
        name="Player"
    )

    player.add_component(Rigidbody2D(
        gravity=900,
        use_gravity=True,
        drag=2.0
    ))

    player.add_component(PlayerController(
        speed=250,
        jump_force=500,
        movement_type="platformer",
        max_jumps=2
    ))

    scene.add_game_object(player)

    ground = create_rectangle(
        x=50, y=500,
        width=800, height=40,
        color=(80, 80, 90),
        name="Ground"
    )
    scene.add_game_object(ground)

    block1 = create_rectangle(x=300, y=380, width=120, height=30, color=(100, 100, 110))
    block2 = create_rectangle(x=500, y=280, width=140, height=30, color=(100, 100, 110))

    scene.add_game_object(block1)
    scene.add_game_object(block2)

    camera_go = GameObject(name="Main Camera")
    camera = camera_go.add_component(Camera(
        target=player,
        follow_speed=6.0,
        smooth_follow=True
    ))
    scene.add_game_object(camera_go)
    scene.set_active_camera(camera)

    return scene