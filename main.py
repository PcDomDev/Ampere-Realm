from engine.core.app import Engine
from scenes.player import build_platformer_scene
from scenes.blocks_test import build_test_scene



def main():
    engine = Engine(width=1920, height=1080, title="Ampere Realm", fps=60)

    scene = build_test_scene()
    engine.load_scene("Blocks Test", scene)

    engine.run()


if __name__ == "__main__":
    main()
