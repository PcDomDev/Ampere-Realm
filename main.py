from engine.core.app import Engine
from engine.core.scene_manager import SceneManager


def main():
    engine = Engine(width=1920, height=1080, title="Ampere Realm", fps=144, fixed_fps=60)

    SceneManager.change_scene()

    engine.run()


if __name__ == "__main__":
    main()
