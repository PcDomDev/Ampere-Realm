import json
import os
import pygame

def load_spritesheet_animations(json_path, image_path):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_json_path = os.path.join(base_dir, json_path)
    full_image_path = os.path.join(base_dir, image_path)

    sheet = pygame.image.load(full_image_path).convert_alpha()

    with open(full_json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    animations = {}
    for frame_name, frame_info in data["frames"].items():
        anim_name = "".join([c for c in frame_name if not c.isdigit()]).lower()

        rect = frame_info["frame"]
        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]

        sprite_surface = sheet.subsurface(pygame.Rect(x, y, w, h))

        if anim_name not in animations:
            animations[anim_name] = []
        animations[anim_name].append(sprite_surface)

    return animations