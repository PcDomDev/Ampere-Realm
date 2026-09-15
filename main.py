from engine.core.app import Engine
from engine.components.camera import Camera
from engine.core.game_object import GameObject
from scenes.player_test import build_platformer_scene



def main():
    engine = Engine(width=1920, height=1080, title="Ampere Realm", fps=60)

    scene = build_platformer_scene()
    engine.load_scene("Player", scene)

    engine.run()


if __name__ == "__main__":
    main()
