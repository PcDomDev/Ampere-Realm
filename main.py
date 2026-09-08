from engine.app import Engine
from engine.components.camera import Camera
from engine.game_object import GameObject
from scenes.game_scene import build_game_scene

def main():
    engine = Engine(width=1920, height=1080, title="My Custom 2D Engine", fps=60)
    scene = build_game_scene()
    engine.load_scene("game_scene", scene)

    engine.run()

if __name__ == "__main__":
    main()