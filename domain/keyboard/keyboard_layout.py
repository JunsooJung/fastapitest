# domain/keyboard/keyboard_layout.py
import json
from .keyboard_config import LAYOUT_FILE, WARP_W, WARP_H
import numpy as np
import cv2

def load_key_layout():
    with open(LAYOUT_FILE, "r", encoding="utf-8") as f:
        raw_layout = json.load(f)

    key_layout = {}
    for k, v in raw_layout.items():
        key_layout[k] = {"x": v[0], "y": v[1], "w": v[2], "h": v[3]}
    return key_layout


def create_empty_keyboard_view():
    """가상 키보드 기본 화면(키 테두리만 있는 상태)"""
    warped_view = np.zeros((WARP_H, WARP_W, 3), dtype=np.uint8)
    return warped_view


def draw_keyboard_layout(warped_view, key_layout):
    """KEY_LAYOUT을 기준으로 키보드 레이아웃 그리기"""
    for key_name, rect in key_layout.items():
        rx, ry, rw, rh = rect["x"], rect["y"], rect["w"], rect["h"]
        cv2.rectangle(warped_view, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 1)
        cv2.putText(
            warped_view,
            key_name,
            (rx + 5, ry + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (200, 200, 200),
            1,
        )
