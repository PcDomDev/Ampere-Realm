from engine.app import Engine
from scenes.menu import menu_scene

def main():
    engine = Engine(width=1920, height=1080, title="Ampere Realm", fps=60)

    menu = menu_scene()
    engine.load_scene("menu", menu)

    engine.run()




    # Добавить больше окмпонентов кнопок юай и вообщем как в юнити
    # Также улучшить физику и убрать баг с дерганием
    # Пофиксить ротейшен и скейл







if __name__ == "__main__":
    main()