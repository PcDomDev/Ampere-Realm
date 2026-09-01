"""Runtime diagnostics for the engine: logging plus an in-game debug overlay.

Two ways to use it:

    debug = DebugManager()          # normally created once by Engine
    debug.log_warning("...")        # instance access

    from engine.debug_manager import DebugManager
    DebugManager.log_warning("...") # static-style access from anywhere,
                                     # e.g. inside a Component that has no
                                     # direct reference to the Engine

Both call paths land on the same instance: whichever DebugManager was
created most recently makes itself the shared instance, and the classmethods
below apply to that one. This mirrors Unity's `Debug.Log(...)` - convenient
for a component-based engine where threading a logger reference through
every single class would be a lot of ceremony for little benefit.

Note the distinction from `engine/utils/warnings.py`: that module is for
construction-time misconfiguration caught once via Python's `warnings`
module (bad anchor string, etc). This module is for runtime, in-game events
- the kind of thing you want visible in an on-screen overlay while the game
is actually running.
"""

import time
from collections import deque

import pygame

from engine.components.box_collider2d import BoxCollider2D


class LogEntry:
    __slots__ = ("level", "message", "source", "timestamp")

    def __init__(self, level, message, source, timestamp):
        self.level = level
        self.message = message
        self.source = source
        self.timestamp = timestamp

    def format(self):
        label = f"[{self.level}]"
        if self.source:
            label += f"[{self.source}]"
        return f"{label} {self.message}"


class DebugManager:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    _LEVEL_COLORS = {
        INFO: (150, 220, 255),
        WARNING: (255, 210, 90),
        ERROR: (255, 110, 110),
    }

    _instance = None

    def __init__(self, history_size=200, overlay_lines=8, print_to_console=True):
        DebugManager._instance = self

        self.print_to_console = print_to_console
        self.overlay_lines = overlay_lines
        self.logs = deque(maxlen=history_size)

        self.show_overlay = False
        self.show_colliders = False

        self.fps = 0.0
        self._fps_timer = 0.0
        self._fps_frame_count = 0

        self._font = None

    # -- singleton-style access --------------------------------------------------

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = DebugManager()
        return cls._instance

    @classmethod
    def log_info(cls, message, source=None):
        cls.instance()._log(cls.INFO, message, source)

    @classmethod
    def log_warning(cls, message, source=None):
        cls.instance()._log(cls.WARNING, message, source)

    @classmethod
    def log_error(cls, message, source=None):
        cls.instance()._log(cls.ERROR, message, source)

    def _log(self, level, message, source):
        entry = LogEntry(level, message, source, time.time())
        self.logs.append(entry)
        if self.print_to_console:
            print(entry.format())

    # -- overlay toggles ----------------------------------------------------------

    def toggle_overlay(self):
        self.show_overlay = not self.show_overlay

    def toggle_colliders(self):
        self.show_colliders = not self.show_colliders

    # -- per-frame bookkeeping --------------------------------------------------

    def update(self, delta_time):
        self._fps_frame_count += 1
        self._fps_timer += delta_time
        if self._fps_timer >= 0.5:
            self.fps = self._fps_frame_count / self._fps_timer
            self._fps_frame_count = 0
            self._fps_timer = 0.0

    # -- drawing --------------------------------------------------------------------

    def draw_overlay(self, screen, scene=None):
        if not self.show_overlay:
            return

        if self._font is None:
            self._font = pygame.font.SysFont("consolas", 16)

        lines = [f"FPS: {self.fps:.1f}"]
        if scene is not None:
            lines.append(f"Scene: {scene.name}  |  Objects: {len(scene.game_objects)}")
        lines.append("F1 overlay  |  F2 colliders")
        lines.append("-" * 32)

        for entry in list(self.logs)[-self.overlay_lines:]:
            lines.append(entry.format())

        padding = 8
        line_height = self._font.get_linesize()
        box_width = 460
        box_height = padding * 2 + line_height * len(lines)

        overlay_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        overlay_surface.fill((15, 15, 20, 180))
        screen.blit(overlay_surface, (10, 10))

        for i, line in enumerate(lines):
            color = (235, 235, 235)
            for level, level_color in self._LEVEL_COLORS.items():
                if line.startswith(f"[{level}]"):
                    color = level_color
                    break
            text_surface = self._font.render(line, True, color)
            screen.blit(text_surface, (10 + padding, 10 + padding + i * line_height))

    def draw_colliders(self, screen, scene, camera=None):
        if not self.show_colliders or scene is None:
            return

        offset = (0, 0)
        if camera is not None:
            cam_offset = camera.get_offset(screen.get_width(), screen.get_height())
            offset = (round(cam_offset.x), round(cam_offset.y))

        for collider in scene.get_components(BoxCollider2D):
            draw_rect = collider.rect.move(-offset[0], -offset[1])
            color = (255, 90, 90) if collider.is_trigger else (90, 255, 120)
            pygame.draw.rect(screen, color, draw_rect, width=2)
