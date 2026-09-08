# PygamE

Небольшой компонентный 2D-движок на Pygame, построенный по модели
GameObject/Component (как в Unity). Каждый объект в игре — это
`GameObject` с `Transform`; поведение (рендер, физика, ввод, анимация,
UI, слежение камеры и т.д.) добавляется через прикрепление `Component`.

*(English version: [README.md](README.md))*

## Быстрый старт

```bash
pip install pygame
python main.py
```

Управление в демо: **A/D** или **←/→** — движение, **Space** — прыжок
(доступен двойной прыжок — нажмите ещё раз в воздухе), **F1** —
отладочная панель, **F2** — отрисовка коллайдеров. Панель в углу
показывает оставшиеся прыжки и кнопку сброса позиции.

## Структура проекта

```
engine/                    сам движок - переиспользуемый, не завязан на конкретную игру
    app.py                    Engine: окно, часы, главный цикл
    game_object.py             GameObject: именованный набор компонентов
    scene.py                    Scene: обновление / коллизии / рендер / UI-проход
    scene_manager.py              SceneManager: хранит именованные сцены
    debug_manager.py               DebugManager: логирование + отладочная панель
    primitives.py                   create_rectangle/square/circle/triangle/line
    components/
        component.py                  базовый класс Component (update_order)
        transform.py                   позиция, поворот, масштаб
        sprite_renderer.py             рисует спрайт (учитывает поворот/масштаб)
        rigidbody2d.py                  гравитация, трение, реакция на столкновения
        box_collider2d.py               хитбокс; твёрдый или триггер
        animator.py                      покадровая анимация спрайтов
        player_controller.py             движение + прыжки (в т.ч. мульти-прыжок)
        camera.py                         следует за целью, смещает рендер
    input/
        key.py                            имена Key.* для кодов клавиш pygame
        input_manager.py                   Input: pressed / just-pressed / мышь
    ui/
        ui_style.py                          общие цвета/шрифты для UI
        ui_element.py                         базовый класс UIElement
        ui_panel.py, ui_text.py, ui_button.py   3 основных UI-виджета
        ui_layout.py                           UILayoutGroup (стек элементов)
    utils/
        vector2.py                              минимальный 2D-вектор
        warnings.py                              категория EngineWarning

scenes/game_scene.py       СОДЕРЖИМОЕ игры: сборка демо-уровня
scripts/                   переиспользуемые игровые скрипты (ResetOnClick, JumpsHUD)
main.py                    только настройка движка + камеры, без игровой логики
```

`engine/` никогда не импортирует из `scenes/` или `scripts/` — движок не
знает, что такое конкретный персонаж, платформа или кнопка *в вашей
игре*. Это знание живёт в `scenes/` (структура уровня) и `scripts/`
(переиспользуемое игровое поведение); `main.py` просто их связывает.

## Основная архитектура

- **GameObject** — имя, `Transform` и список `Component`. Почти без
  собственного поведения.
- **Component** — базовый класс для всего, что можно прикрепить. Имеет
  `start()` (выполняется один раз) и `update(delta_time)` (каждый кадр,
  пока `enabled`). `update_order` (по умолчанию `0`) задаёт порядок
  выполнения компонентов одного объекта независимо от порядка их
  добавления:

  | Компонент | update_order |
  |---|:---:|
  | `Rigidbody2D` | -100 |
  | `BoxCollider2D` | -90 |
  | *(игровой код, UI)* | 0 |
  | `Camera` | 100 |

- **Scene** — хранит список GameObject; каждый кадр обновляет их,
  обрабатывает триггеры, затем рисует мир (со смещением камеры) и в
  конце — UI (в экранных координатах, всегда поверх всего, камера на
  него не влияет).
- **Engine** — окно, часы, главный цикл. Ограничивает `delta_time`
  сверху 50 мс, чтобы зависание не отдало физике один огромный, опасный
  шаг.

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

Каждый `GameObject` получает его автоматически — `position` (`Vector2`),
`rotation` (градусы, по часовой стрелке), `scale` (`Vector2`, 1.0 =
исходный размер). `GameObject.x`/`.y` остаются алиасами для
`transform.position.x`/`.y`.

`SpriteRenderer` теперь учитывает поворот и масштаб (вращает/масштабирует
вокруг центра спрайта, результат кэшируется, так что статичный объект не
пересчитывается каждый кадр):

```python
obj.transform.rotation = 45          # градусы, по часовой
obj.transform.scale.x = 2.0          # в 2 раза шире
```

Важно: размер `BoxCollider2D` не зависит от `transform.scale` —
визуальное масштабирование объекта не меняет размер его хитбокса.
Вызовите `collider.set_size(w, h)`, если нужно, чтобы они совпадали.

## Справочник компонентов

### SpriteRenderer

```python
SpriteRenderer(sprite=None, z_index=0, offset_y=0)
```
Рисует `sprite` в позиции transform'а, с учётом поворота/масштаба.
`z_index` задаёт порядок слоёв; внутри одного слоя объекты сортируются по
`position.y + offset_y` (те, что ниже на экране, рисуются поверх).

### Rigidbody2D

```python
Rigidbody2D(gravity=500, gravity_scale=1.0, drag=0.0, mass=1.0,
            use_gravity=True, is_kinematic=False, terminal_velocity=1000)
```
Гравитация + трение + реакция на столкновения (AABB). Чтобы объект
реально с чем-то сталкивался, на нём должен быть `BoxCollider2D`.

| Поле | Описание |
|---|---|
| `velocity` | `Vector2`, пикс/сек. |
| `is_grounded` | `True`, пока объект стоит на чём-то твёрдом. |
| `add_impulse(ix, iy)` | Мгновенно: `Δv = impulse / mass`. |
| `add_force(fx, fy, delta_time)` | Постоянно: `Δv = (force/mass) * dt` — вызывать каждый кадр. |
| `stop()` | Обнуляет скорость. |

### BoxCollider2D

```python
BoxCollider2D(size=None, offset_x=0, offset_y=0, anchor="topleft", is_trigger=False)
```
Прямоугольный хитбокс — твёрдый, либо `is_trigger=True` для обнаружения
пересечений без физической блокировки. По возможности указывайте
`size=(w, h)` явно; иначе размер измеряется один раз по спрайту при
`start()` и **фиксируется** (больше никогда не пересчитывается, даже
если спрайт потом поменяет размер — именно это делает столкновения
стабильными при использовании с `Animator`). `anchor` — одно из 9 имён
привязки pygame; неверное значение вызывает `EngineWarning` и
откатывается на `"topleft"`.

```python
collider.on_trigger_enter.append(lambda trigger, other: print("касание!"))
```

### Animator

```python
Animator(animations=None, default_animation=None, frame_duration=0.1)
```
`animations` — это `{имя: [surface, ...]}`. `play(name, loop=True,
reverse=False)` безопасно вызывать каждый кадр с нужной анимацией —
повторные вызовы с тем же, уже проигрываемым именем не перезапускают её.

### PlayerController

```python
PlayerController(speed=200, jump_force=350, movement_type="top_down",
                  keybinds=None, anim_map=None,
                  coyote_time=0.1, jump_buffer_time=0.1, max_jumps=1)
```
`movement_type`: `"top_down"` (движение в 4/8 направлений, без гравитации)
или `"platformer"` (бег + прыжок через `Rigidbody2D`).

**Двойной / мульти-прыжок**: `max_jumps` задаёт, сколько раз персонаж
может прыгнуть, прежде чем ему нужно снова коснуться земли — `1` (по
умолчанию) это обычный одиночный прыжок, `2` — двойной, `3`+ работает
так же. Каждый прыжок, кроме первого, доступен сразу в воздухе (без
ограничения coyote-time, так как игрок сознательно использует
дополнительный прыжок); счётчик прыжков восстанавливается в момент
приземления. Читайте `controller.jumps_remaining` для отображения в UI.

```python
character.add_component(PlayerController(
    speed=200, jump_force=500, movement_type="platformer", max_jumps=2,
))
```

`keybinds` принимает константы `Key.*`, «сырые» константы `pygame.K_*`
или строки — взаимозаменяемо (см. раздел «Система ввода» ниже):

```python
PlayerController(keybinds={
    "left": ["a", Key.LEFT], "right": ["d", Key.RIGHT], "jump": [Key.SPACE],
})
```

Расширяйте через наследование и переопределение отдельного хука, а не
всего класса — `_on_jump()`, `_can_jump()`/`_wants_to_jump()`,
`_play_platformer_animation()`, `_read_move_axis()`.

### Camera

```python
Camera(target=None, follow_speed=5.0, smooth_follow=True, position=None)
```
`Component` на собственном `GameObject`. Никогда не двигает свою цель —
она отслеживает собственную `position`, а `Scene.render()` вычитает
получившееся смещение из мировой позиции каждого спрайта (включая саму
цель) — именно это заставляет мир плавно скроллиться вокруг неё.
`smooth_follow=True` использует экспоненциальное сглаживание, не
зависящее от частоты кадров (не может «перелететь» цель ни при каком
FPS). При `target=None` `get_offset()` всегда возвращает `(0, 0)` — мир
рисуется без каких-либо смещений, точно как без камеры вообще.

```python
camera_go = GameObject(name="Main Camera")
camera = camera_go.add_component(Camera(target=character, follow_speed=6.0))
scene.add_game_object(camera_go)
scene.set_active_camera(camera)
```

## Система ввода

`engine/input/key.py` + `engine/input/input_manager.py`. Три
взаимозаменяемых способа указать клавишу:

```python
Key.W          # через атрибут
"w"            # строка, регистр не важен
pygame.K_w     # «сырая» константа pygame - Key.W это буквально то же значение
```

`Input` (принадлежит `Engine`, обновляется раз в кадр) добавляет
определение «именно в этом кадре» поверх «сырого» состояния pygame
(«зажато сейчас»):

```python
from engine.input.input_manager import Input
from engine.input.key import Key

Input.is_pressed(Key.W)          # зажато прямо сейчас
Input.is_just_pressed(Key.SPACE) # true только в кадре самого нажатия
Input.is_just_released(Key.SPACE)

Input.mouse_position()
Input.is_mouse_pressed(0)          # 0 = левая, 1 = средняя, 2 = правая
Input.is_mouse_just_pressed(0)
Input.is_mouse_just_released(0)
```

Работает откуда угодно (`Input.is_pressed(...)`) либо через
`engine.input` (экземпляр, созданный `Engine`) — та же схема двойного
доступа, что и у `DebugManager`.

## Система UI

Виджеты в экранных координатах, не зависящие от камеры, рисуются после
мира отдельным проходом. Позиция UI-элемента берётся из `Transform` его
`GameObject`, как и у всего остального — просто трактуется как пиксели
экрана, а не мировые координаты.

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
label.add_component(UIText(text="Счёт: 0", align="left"))
scene.add_game_object(label)

button_go = GameObject(x=20, y=60, name="StartButton")
button = button_go.add_component(UIButton(text="Старт", width=150, height=36))
button.on_click.append(lambda b: print("нажато!"))
scene.add_game_object(button_go)
```

| Класс | Назначение |
|---|---|
| `UIElement` | Базовый класс (`width`, `height`, `visible`, `draw_order`, `.rect`, `contains_point()`). |
| `UIPanel` | Простой прямоугольный фон, опционально с рамкой. |
| `UIText` | Рисует строку; `set_text()` для обновления; `align="left"/"center"/"right"`. |
| `UIButton` | Прямоугольник + текст; отслеживает `is_hovered`/`is_pressed`; вызывает `on_click` (список, как `on_trigger_enter`) при нажатии-и-отпускании над кнопкой. |
| `UILayoutGroup` | `direction="vertical"/"horizontal"`, `spacing=8`; `add_item(game_object)` выстраивает UI-объекты относительно позиции самого layout'а (в этом движке нет иерархии transform'ов родитель-потомок, поэтому это просто помощник для позиционирования, а не настоящая вложенность). |
| `UIStyle` | Общие `background_color`, `border_color`/`width`, `text_color`, `font_name`/`size`, `hover_color`, `pressed_color` — передайте один `style=` вместо повторения цветов везде. |

Не полноценный движок тем и не миллион виджетов — только необходимое,
как и просилось, под задачи небольшой 2D-игры (меню, HUD, простые
диалоги).

## Примитивы

`engine/primitives.py` — создание объектов-фигур без прямого обращения к
функциям рисования Pygame:

```python
from engine.primitives import create_rectangle, create_square, create_circle, create_triangle, create_line

create_rectangle(x=0, y=0, width=100, height=20, color=(200,200,200), add_collider=True, add_rigidbody=False)
create_square(x=0, y=0, size=50, color=(200,200,200))
create_circle(x=0, y=0, radius=25, color=(200,200,200))
create_triangle(x=0, y=0, size=50, color=(200,200,200))
create_line(x=0, y=0, length=100, thickness=4, vertical=False)  # без коллайдера по умолчанию
```

Каждая функция возвращает готовый к добавлению `GameObject`
(`SpriteRenderer` и, для твёрдых фигур, соответствующий `BoxCollider2D`
по умолчанию). Обратите внимание: коллайдер по умолчанию для
`create_circle`/`create_triangle` — это **приближение** ограничивающим
прямоугольником: в движке есть только осевыровненный box-коллайдер, нет
коллайдера-круга или полигона. Передайте `add_collider=False`, если это
приближение не подходит для вашей игры.

(Отдельного `create_cube()` нет — движок двумерный, поэтому вместо
«куба» предоставлены 2D-аналоги: `create_rectangle`/`create_square`.)

## Стабильность физики

Приземление/покой были перепроверены на 120+ автоматических проверках
при широком разбросе параметров: гравитация 300–3000, размеры объектов
16–200 пикс., масса 0.5–10, частота кадров 30–144 FPS, объект на
статичном полу, объект на *другом динамическом* объекте, стек из трёх
уровней, и проверка на дрейф за 10 000 кадров непрерывной работы. Все
случаи стабилизируются в точной, устойчивой позиции покоя без мерцания
`is_grounded` и без видимого дрожания. Механизм — ниже.

**Почему коррекция столкновений теперь точная:** `BoxCollider2D.rect` —
это `pygame.Rect`, который округляет каждую координату до ближайшего
целого. Вычисление коррекции позиции на основе уже округлённого rect'а
(вычитание целочисленного перекрытия из вещественной позиции) теряет
долю пикселя, которая не компенсируется обратно — за много кадров это
проявляется как заметное дрожание. Вместо этого коррекция столкновений
«примагничивает» объект напрямую к точному краю *другого* коллайдера,
используя полную вещественную позицию transform'а
(`BoxCollider2D.snap_bottom_to`/`snap_top_to`/`snap_left_to`/
`snap_right_to`), полностью минуя эту потерю точности от округления.
Небольшая «проверка земли под ногами»
(`Rigidbody2D.GROUND_PROBE_DISTANCE`, 4 пикс.) дополнительно не даёт
`is_grounded` мерцать между кадрами из-за шума округления до пикселя.

## Как расширять движок

- **Новый компонент** — унаследуйте от `Component`, переопределите
  `start()`/`update()`. Место в `engine/components/` — только если
  компонент общий (не завязан на конкретную игру); иначе это **скрипт**
  (ниже).
- **Новый игровой скрипт** (монетка, ИИ врага, обновление HUD) —
  унаследуйте от `Component`, положите в `scripts/`. Смотрите
  `scripts/reset_on_click.py` и `scripts/jumps_hud.py` — два небольших
  законченных примера.
- **Новый уровень** — напишите новую функцию `build_*_scene()` в
  `scenes/`, затем в `main.py`:
  `engine.load_scene("имя", build_your_scene())`.
- **Расширение PlayerController** — наследуйтесь и переопределяйте один
  хук (см. выше), а не копируйте весь класс.

## Что изменилось в этом обновлении

- Конкретные объекты старого демо ("Player"/"Coin") и их спрайты
  полностью удалены; демо-сцена теперь строится через
  `engine.primitives` (без каких-либо внешних файлов изображений), а
  управляемый объект называется обобщённо — `"Character"`.
- Добавлена **система UI** (`engine/ui/`): `UIPanel`, `UIText`,
  `UIButton`, `UILayoutGroup`, `UIStyle`.
- Добавлена **система ввода** (`engine/input/`): удобные имена `Key` +
  менеджер `Input` с pressed/just-pressed/just-released для клавиатуры и
  мыши. `PlayerController` теперь работает через неё вместо прямых
  вызовов pygame.
- Добавлены **примитивы** (`engine/primitives.py`):
  `create_rectangle`/`create_square`/`create_circle`/`create_triangle`/
  `create_line`.
- **Двойной / мульти-прыжок**: `PlayerController(max_jumps=N)`.
- **Поворот и масштаб теперь реально отрисовываются** — `SpriteRenderer`
  поворачивает/масштабирует спрайты согласно `Transform`, с кэшированием
  для производительности.
- **Физика перепроверена**, найден и исправлен ещё один тонкий баг:
  точное (без округления) «примагничивание» при коррекции столкновений
  (`BoxCollider2D.snap_*_to`) заменило прежнее вычитание округлённого
  перекрытия, которое при определённых условиях давало небольшой, но
  реальный суб-пиксельный дрейф. Подробности — в разделе «Стабильность
  физики» выше.
- Документация объединена в этот единственный файл (+ его английская
  версия, `README.md`) вместо того, чтобы быть раскиданной по нескольким
  файлам.
- Добавлен `.gitignore` для GitHub.
