# PygamE

A small, component-based 2D engine built on Pygame, in the style of
Unity's GameObject/Component model. Every object in the world is a
`GameObject` with a `Transform`; behaviour (rendering, physics, input,
animation, UI, camera-following, ...) comes from attaching `Component`s
to it.

*(Русская версия: [README.ru.md](README.ru.md))*

## Quick start

```bash
pip install pygame
python main.py
```

Demo controls: **A/D** or **←/→** to move, **Space** to jump (double-jump
enabled - press it again in mid-air), **F1** toggles the debug overlay,
**F2** toggles collider outlines. The on-screen panel shows your
remaining jumps and a button to reset your position.

## Project structure

```
engine/                    the engine itself - reusable, game-agnostic
    app.py                    Engine: window, clock, main loop
    game_object.py             GameObject: a named bag of components
    scene.py                    Scene: update / collide / render / UI pass
    scene_manager.py              SceneManager: owns named scenes
    debug_manager.py               DebugManager: logging + debug overlay
    primitives.py                   create_rectangle/square/circle/triangle/line
    components/
        component.py                  Component base class (update_order)
        transform.py                   position, rotation, scale
        sprite_renderer.py             draws a sprite (rotation/scale aware)
        rigidbody2d.py                  gravity, drag, collision response
        box_collider2d.py               the hitbox; solid or trigger
        animator.py                      frame-based sprite animation
        player_controller.py             movement + jumping (incl. multi-jump)
        camera.py                         follows a target, offsets rendering
    input/
        key.py                            Key.* names for pygame key codes
        input_manager.py                   Input: pressed / just-pressed / mouse
    ui/
        ui_style.py                          shared colours/fonts for UI
        ui_element.py                         UIElement base class
        ui_panel.py, ui_text.py, ui_button.py   the 3 core UI widgets
        ui_layout.py                           UILayoutGroup (stacking)
    utils/
        vector2.py                              minimal 2D vector
        warnings.py                              EngineWarning category

scenes/game_scene.py       game CONTENT: builds the demo level
scripts/                   reusable gameplay scripts (ResetOnClick, JumpsHUD)
main.py                    engine setup + camera init only, no game logic
```

`engine/` never imports from `scenes/` or `scripts/` - it has no idea what
a specific character, platform, or button in *your* game is. That
knowledge lives in `scenes/` (level layout) and `scripts/` (reusable
gameplay behaviours); `main.py` just wires the two together.

## Core architecture

- **GameObject** - a name, a `Transform`, and a list of `Component`s.
  Almost no behaviour of its own.
- **Component** - the base class for everything attachable. Has
  `start()` (runs once) and `update(delta_time)` (runs every frame while
  `enabled`). `update_order` (default `0`) controls execution order across
  a GameObject's components, regardless of attach order:

  | Component | update_order |
  |---|:---:|
  | `Rigidbody2D` | -100 |
  | `BoxCollider2D` | -90 |
  | *(gameplay code, UI)* | 0 |
  | `Camera` | 100 |

- **Scene** - owns a list of GameObjects; each frame updates them,
  resolves trigger overlaps, then renders the world (camera-offset) and
  finally the UI (screen-space, always on top, never offset by the
  camera).
- **Engine** - the window, the clock, the main loop. Clamps `delta_time`
  to 50ms so a stall can't hand physics one giant, unsafe step.

```python
from engine.game_object import GameObject
from engine.components.sprite_renderer import SpriteRenderer
from engine.components.rigidbody2d import Rigidbody2D

obj = GameObject(x=100, y=100, name="Box")
obj.add_component(SpriteRenderer(sprite=my_surface))
obj.add_component(Rigidbody2D(gravity=900, use_gravity=True))
scene.add_game_object(obj)
```

## Transform

Every `GameObject` gets one automatically - `position` (`Vector2`),
`rotation` (degrees, clockwise-positive), `scale` (`Vector2`, 1.0 =
original size). `GameObject.x`/`.y` remain as aliases for
`transform.position.x`/`.y`.

`SpriteRenderer` now honors rotation and scale (rotating/scaling around
the sprite's center, cached so a static object isn't re-transformed every
frame):

```python
obj.transform.rotation = 45          # degrees, clockwise
obj.transform.scale.x = 2.0          # 2x wide
```

Note: `BoxCollider2D`'s size is independent of `transform.scale` - scaling
an object visually does not resize its hitbox. Call `collider.set_size(w,
h)` if you need the two to match.

## Components reference

### SpriteRenderer

```python
SpriteRenderer(sprite=None, z_index=0, offset_y=0)
```
Draws `sprite` at the transform's position, honoring rotation/scale.
`z_index` controls layering; within the same layer, objects are sorted by
`position.y + offset_y` (lower on screen draws in front).

### Rigidbody2D

```python
Rigidbody2D(gravity=500, gravity_scale=1.0, drag=0.0, mass=1.0,
            use_gravity=True, is_kinematic=False, terminal_velocity=1000)
```
Gravity + drag + AABB collision response. Requires a `BoxCollider2D` on
the same object to actually collide with anything.

| Member | Description |
|---|---|
| `velocity` | `Vector2`, px/s. |
| `is_grounded` | `True` while resting on something solid. |
| `add_impulse(ix, iy)` | Instant: `Δv = impulse / mass`. |
| `add_force(fx, fy, delta_time)` | Continuous: `Δv = (force/mass) * dt` - call every frame. |
| `stop()` | Zeroes velocity. |

### BoxCollider2D

```python
BoxCollider2D(size=None, offset_x=0, offset_y=0, anchor="topleft", is_trigger=False)
```
An axis-aligned hitbox - solid, or `is_trigger=True` for overlap-only.
Pass `size=(w, h)` explicitly when you can; otherwise it's measured once
from the sprite at `start()` and **locked** (never re-measured, even if
the sprite later changes size - this is what keeps collision stable when
combined with an `Animator`). `anchor` is one of pygame's 9 named anchors
- an invalid one raises an `EngineWarning` and falls back to `"topleft"`.

```python
collider.on_trigger_enter.append(lambda trigger, other: print("touched!"))
```

### Animator

```python
Animator(animations=None, default_animation=None, frame_duration=0.1)
```
`animations` is `{name: [surface, ...]}`. `play(name, loop=True,
reverse=False)` is safe to call every frame with the intended animation -
repeated calls with the same, still-playing name don't restart it.

### PlayerController

```python
PlayerController(speed=200, jump_force=350, movement_type="top_down",
                  keybinds=None, anim_map=None,
                  coyote_time=0.1, jump_buffer_time=0.1, max_jumps=1)
```
`movement_type`: `"top_down"` (4/8-directional, no gravity) or
`"platformer"` (run + gravity-driven jump via `Rigidbody2D`).

**Multi-jump / double jump**: `max_jumps` sets how many times the
character can jump before needing to touch the ground again - `1` (the
default) is a normal single jump, `2` is a double jump, `3`+ works the
same way. Every jump after the first is available immediately while
airborne (no coyote-time restriction, since the player is deliberately
using an extra jump); the jump count refills the instant the character
lands. Read `controller.jumps_remaining` for a UI readout.

```python
character.add_component(PlayerController(
    speed=200, jump_force=500, movement_type="platformer", max_jumps=2,
))
```

`keybinds` accepts `Key.*` constants, raw `pygame.K_*` constants, or
strings interchangeably (see Input System below):

```python
PlayerController(keybinds={
    "left": ["a", Key.LEFT], "right": ["d", Key.RIGHT], "jump": [Key.SPACE],
})
```

Extend by subclassing and overriding a hook rather than the whole class -
`_on_jump()`, `_can_jump()`/`_wants_to_jump()`,
`_play_platformer_animation()`, `_read_move_axis()`.

### Camera

```python
Camera(target=None, follow_speed=5.0, smooth_follow=True, position=None)
```
A `Component` on its own `GameObject`. Never moves its target - it tracks
its own `position` and `Scene.render()` subtracts the resulting offset
from every sprite's world position (target included), which is what makes
the world scroll smoothly around it. `smooth_follow=True` uses
frame-rate-independent exponential easing (cannot overshoot, at any frame
rate). With `target=None`, `get_offset()` always returns `(0, 0)` - the
world renders completely unshifted, identical to having no camera at all.

```python
camera_go = GameObject(name="Main Camera")
camera = camera_go.add_component(Camera(target=character, follow_speed=6.0))
scene.add_game_object(camera_go)
scene.set_active_camera(camera)
```

## Input system

`engine/input/key.py` + `engine/input/input_manager.py`. Three
interchangeable ways to refer to a key:

```python
Key.W          # attribute access
"w"            # case-insensitive string
pygame.K_w     # raw pygame constant - Key.W literally *is* this value
```

`Input` (owned by `Engine`, updated once per frame) adds "this frame only"
edge detection on top of pygame's raw "currently held" state:

```python
from engine.input.input_manager import Input
from engine.input.key import Key

Input.is_pressed(Key.W)          # held down right now
Input.is_just_pressed(Key.SPACE) # true only on the single press frame
Input.is_just_released(Key.SPACE)

Input.mouse_position()
Input.is_mouse_pressed(0)          # 0 = left, 1 = middle, 2 = right
Input.is_mouse_just_pressed(0)
Input.is_mouse_just_released(0)
```

Works from anywhere (`Input.is_pressed(...)`) or via `engine.input`
(the instance `Engine` created) - same dual-access pattern as
`DebugManager`.

## UI system

Screen-space widgets, unaffected by the camera, drawn after the world in
their own pass. A UI element's position comes from its `GameObject`'s
`Transform`, same as everything else - it's just interpreted as screen
pixels instead of world coordinates.

```python
from engine.ui.ui_panel import UIPanel
from engine.ui.ui_text import UIText
from engine.ui.ui_button import UIButton
from engine.ui.ui_layout import UILayoutGroup
from engine.ui.ui_style import UIStyle

panel = GameObject(x=10, y=10, name="HUD")
panel.add_component(UIPanel(width=200, height=100))
scene.add_game_object(panel)

label = GameObject(x=20, y=20, name="ScoreLabel")
label.add_component(UIText(text="Score: 0", align="left"))
scene.add_game_object(label)

button_go = GameObject(x=20, y=60, name="StartButton")
button = button_go.add_component(UIButton(text="Start", width=150, height=36))
button.on_click.append(lambda b: print("clicked!"))
scene.add_game_object(button_go)
```

| Class | Purpose |
|---|---|
| `UIElement` | Base class (`width`, `height`, `visible`, `draw_order`, `.rect`, `contains_point()`). |
| `UIPanel` | A plain rectangular background, optionally bordered. |
| `UIText` | Renders a string; `set_text()` to update it; `align="left"/"center"/"right"`. |
| `UIButton` | Rectangle + label; tracks `is_hovered`/`is_pressed`; fires `on_click` (a list, like `on_trigger_enter`) on press-then-release-while-still-hovering. |
| `UILayoutGroup` | `direction="vertical"/"horizontal"`, `spacing=8`; `add_item(game_object)` stacks UI GameObjects relative to the layout's own position (this engine has no parent-child transform hierarchy, so this is a positioning helper, not true nesting). |
| `UIStyle` | Shared `background_color`, `border_color`/`width`, `text_color`, `font_name`/`size`, `hover_color`, `pressed_color` - pass one `style=` to any of the above instead of repeating colours everywhere. |

Not a full theming engine, and not a million widgets - the essentials
requested, matching what a small 2D game typically needs (menus, HUDs,
simple dialogs).

## Primitives

`engine/primitives.py` - build shape-based GameObjects without touching
Pygame's drawing calls directly:

```python
from engine.primitives import create_rectangle, create_square, create_circle, create_triangle, create_line

create_rectangle(x=0, y=0, width=100, height=20, color=(200,200,200), add_collider=True, add_rigidbody=False)
create_square(x=0, y=0, size=50, color=(200,200,200))
create_circle(x=0, y=0, radius=25, color=(200,200,200))
create_triangle(x=0, y=0, size=50, color=(200,200,200))
create_line(x=0, y=0, length=100, thickness=4, vertical=False)  # no collider by default
```

Each returns a ready-to-add `GameObject` (a `SpriteRenderer` and, for the
solid shapes, a matching `BoxCollider2D` by default). Note:
`create_circle`/`create_triangle`'s default collider is a bounding-box
*approximation* - this engine only has an axis-aligned box collider, no
circle/polygon collider. Pass `add_collider=False` if that approximation
doesn't work for your game.

(There's no `create_cube()` - this is a 2D engine, so the 2D equivalent,
`create_rectangle`/`create_square`, is what's provided.)

## Physics stability

Landing/resting was re-verified with 120+ automated checks across a wide
parameter sweep: gravity 300-3000, object sizes 16-200px, masses 0.5-10,
frame rates 30-144 FPS, single objects on a static floor, an object
resting on *another dynamic* object, a three-high stack, and a
10,000-frame long-run check for drift. All settle to an exact, stable
resting position with no flicker in `is_grounded` and no visible jitter.
See "Why collision correction is exact" below for the mechanism.

**Why collision correction is exact:** `BoxCollider2D.rect` is a
`pygame.Rect`, which rounds every coordinate to the nearest int. Deriving
a position correction from that already-rounded rect (subtracting an
integer overlap from a float position) loses a fraction of a pixel that
doesn't cancel back out - across many frames this shows up as visible
jitter. Collision resolution instead snaps directly to the *other*
collider's exact edge using the full float transform position
(`BoxCollider2D.snap_bottom_to`/`snap_top_to`/`snap_left_to`/
`snap_right_to`), bypassing that rounding loss entirely. A small ground
probe (`Rigidbody2D.GROUND_PROBE_DISTANCE`, 4px) additionally prevents
`is_grounded` from flickering frame-to-frame purely due to sub-pixel
rounding noise.

## Extending the engine

- **New component** - subclass `Component`, override `start()`/`update()`.
  Belongs in `engine/components/` only if it's generic (no knowledge of
  your specific game); otherwise it's a **script** (below).
- **New gameplay script** (a coin, an enemy AI, a HUD updater) - subclass
  `Component`, put it in `scripts/`. See `scripts/reset_on_click.py` and
  `scripts/jumps_hud.py` for two small, complete examples.
- **New level** - write a new `build_*_scene()` function in `scenes/`,
  then in `main.py`: `engine.load_scene("name", build_your_scene())`.
- **Extending PlayerController** - subclass it and override a hook (see
  above) rather than copying the whole class.

## What changed in this update

- Removed the old demo's specific "Player"/"Coin" objects and their
  sprite assets entirely; the demo scene is now built from
  `engine.primitives` (no external image dependency at all) and the
  controllable object is a generic `"Character"`.
- **UI system** added (`engine/ui/`): `UIPanel`, `UIText`, `UIButton`,
  `UILayoutGroup`, `UIStyle`.
- **Input system** added (`engine/input/`): `Key` friendly names +
  `Input` manager with press/just-pressed/just-released for keyboard and
  mouse. `PlayerController` now reads through this instead of calling
  pygame directly.
- **Primitives** added (`engine/primitives.py`):
  `create_rectangle`/`create_square`/`create_circle`/`create_triangle`/
  `create_line`.
- **Double/multi-jump**: `PlayerController(max_jumps=N)`.
- **Rotation and scale are now rendered** - `SpriteRenderer` rotates/scales
  sprites to match `Transform`, cached for performance.
- **Physics re-verified**, and one more subtle bug fixed: exact
  (unrounded) collision-correction snapping (`BoxCollider2D.snap_*_to`)
  replaces the previous rounded-overlap subtraction, which had a small
  but real sub-pixel drift under certain conditions. See "Physics
  stability" above.
- Documentation consolidated into this single file (+ its Russian
  translation, `README.ru.md`) instead of being spread across several
  files.
- Added `.gitignore` for GitHub.
