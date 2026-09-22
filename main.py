from engine.core.app import Engine
from engine.core.scene_manager import SceneManager
from scenes.menu import MenuScene

def main():
    engine = Engine(width=1920, height=1080, title="Ampere Realm", fps=144, fixed_fps=60)

    SceneManager.change_scene(MenuScene)

    engine.run()


if __name__ == "__main__":
    main()
