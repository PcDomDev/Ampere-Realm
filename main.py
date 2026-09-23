from engine.core.app import Engine
from engine.core.scene_manager import SceneManager
from scenes.blocks_test import BlocksTestScene


def main():
    engine = Engine(width=1920, height=1080, title="Ampere Realm", fps=144)

    SceneManager.change_scene(BlocksTestScene)

    engine.run()


if __name__ == "__main__":
    main()
