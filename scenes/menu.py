import pygame
from engine.scene import Scene
from engine.game_object import GameObject
from engine.components.sprite_renderer import SpriteRenderer
from engine.components.box_collider2d import BoxCollider2D
from engine.components.rigidbody2d import Rigidbody2D

def menu_scene():
    menu = Scene(name="menu")

    # Platform
    platform_surface = pygame.Surface((500, 50))
    platform_surface.fill((255, 255, 255))
    platform = GameObject(name="GroundPlatform", x=700, y=900)
    platform.add_component(SpriteRenderer(sprite=platform_surface))
    platform.add_component(BoxCollider2D(size=(500, 50), anchor="topleft"))
    menu.add_game_object(platform)

    # Cubes
    cube_surface = pygame.Surface((50, 50))
    cube_surface.fill((255, 0, 0))
    cube = GameObject(name="Cube1", x=950, y=800)
    cube.add_component(SpriteRenderer(sprite=cube_surface))
    cube.add_component(BoxCollider2D(size=(50, 50), anchor="topleft"))
    cube.add_component(Rigidbody2D(gravity=900, use_gravity=True, drag=3.0))
    menu.add_game_object(cube)

    cube_1_surface = pygame.Surface((50, 50))
    cube_1_surface.fill((255, 0, 0))
    cube_1 = GameObject(name="Cube_1", x=990, y=700)
    cube_1.transform.rotation += 45
    cube_1.add_component(SpriteRenderer(sprite=cube_1_surface))
    cube_1.add_component(BoxCollider2D(size=(50, 50), anchor="topleft"))
    cube_1.add_component(Rigidbody2D(gravity=900, use_gravity=True, drag=3.0))


    menu.add_game_object(cube_1)

    return menu