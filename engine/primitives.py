"""Factory functions for building simple shape-based GameObjects without
touching Pygame's drawing calls yourself.

Each function draws the shape onto a new Surface, builds a GameObject with
a SpriteRenderer for it, and (for the solid shapes) attaches a matching
BoxCollider2D by default - similar to how a primitive comes with a fitting
collider already attached in engines like Unity. All of it is optional
(`add_collider=False`/`add_rigidbody=True` etc.) and every function just
returns the GameObject - none of them add it to a scene for you, so you
still call `scene.add_game_object(...)` yourself, same as building one by
hand.

Note on `create_circle` / `create_triangle`: this engine only has an
axis-aligned box collider (BoxCollider2D) - there's no circle or polygon
collider. Their default collider is therefore a bounding-box
*approximation* (a square around the circle, a square around the
triangle), which is close enough for many games but will feel slightly
"off" for precise circular collision (e.g. a ball that should roll past a
corner it hasn't visually touched yet). Pass `add_collider=False` and
attach your own approximation if that matters for your game.
"""
import pygame

from engine.components.box_collider2d import BoxCollider2D
from engine.components.rigidbody2d import Rigidbody2D
from engine.components.sprite_renderer import SpriteRenderer
from engine.game_object import GameObject


def create_rectangle(x=0, y=0, width=50, height=50, color=(200, 200, 200),
                      name="Rectangle", add_collider=True, add_rigidbody=False,
                      border_radius=0):
    """A filled rectangle GameObject."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, surface.get_rect(), border_radius=border_radius)

    go = GameObject(x=x, y=y, name=name)
    go.add_component(SpriteRenderer(sprite=surface))
    if add_collider:
        go.add_component(BoxCollider2D(size=(width, height), anchor="topleft"))
    if add_rigidbody:
        go.add_component(Rigidbody2D())
    return go


def create_square(x=0, y=0, size=50, color=(200, 200, 200), name="Square",
                   add_collider=True, add_rigidbody=False):
    """A filled square - a thin convenience wrapper over create_rectangle
    for the common case of width == height."""
    return create_rectangle(x=x, y=y, width=size, height=size, color=color,
                             name=name, add_collider=add_collider,
                             add_rigidbody=add_rigidbody)


def create_circle(x=0, y=0, radius=25, color=(200, 200, 200), name="Circle",
                   add_collider=True, add_rigidbody=False):
    """A filled circle GameObject. See the module docstring above for the
    bounding-box collider approximation this uses by default."""
    diameter = radius * 2
    surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (radius, radius), radius)

    go = GameObject(x=x, y=y, name=name)
    go.add_component(SpriteRenderer(sprite=surface))
    if add_collider:
        go.add_component(BoxCollider2D(size=(diameter, diameter), anchor="topleft"))
    if add_rigidbody:
        go.add_component(Rigidbody2D())
    return go


def create_triangle(x=0, y=0, size=50, color=(200, 200, 200), name="Triangle",
                     add_collider=True, add_rigidbody=False):
    """An upward-pointing triangle, inscribed in a `size` x `size` box.
    Collider is the bounding box - same caveat as create_circle."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    points = [(size / 2, 0), (size, size), (0, size)]
    pygame.draw.polygon(surface, color, points)

    go = GameObject(x=x, y=y, name=name)
    go.add_component(SpriteRenderer(sprite=surface))
    if add_collider:
        go.add_component(BoxCollider2D(size=(size, size), anchor="topleft"))
    if add_rigidbody:
        go.add_component(Rigidbody2D())
    return go


def create_line(x=0, y=0, length=100, thickness=4, color=(200, 200, 200),
                 name="Line", vertical=False):
    """A straight line segment, drawn as a thin filled rectangle. No
    collider by default - lines are usually visual (dividers, rails), not
    solid obstacles. Pass the result through your own BoxCollider2D setup
    if you need one to be solid."""
    width, height = (thickness, length) if vertical else (length, thickness)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(color)

    go = GameObject(x=x, y=y, name=name)
    go.add_component(SpriteRenderer(sprite=surface))
    return go
