from engine.components.sprite_renderer import SpriteRenderer
from engine.core.game_object import GameObject
from engine.core.scene import Scene
from engine.core.scene_manager import SceneManager
from engine.ui.ui_button import UIButton
from engine.ui.ui_text import UIText
import pygame.image

class MenuScene(Scene):
    def start(self):
        super().start()
        exit_button = GameObject(700, 650, name="Exit Button")
        exit_button.add_component(SpriteRenderer(sprite=pygame.image.load("assets/ui/buttons/exit.png"), anchor="center"))
        self.add_game_object(exit_button)

        play_button = GameObject(700, 400, name="Play Button")
        play_button.add_component(SpriteRenderer(sprite=pygame.image.load("assets/ui/buttons/play.png"), anchor="center"))
        self.add_game_object(play_button)

        options_button = GameObject(700, 500, name="Options Button")
        options_button.add_component(SpriteRenderer(sprite=pygame.image.load("assets/ui/buttons/options.png"), anchor="center"))
        self.add_game_object(options_button)
