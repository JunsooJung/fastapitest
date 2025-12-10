# domain/keyboard/keyboard_config.py
import os
import torch

current_dir = os.path.dirname(os.path.abspath(__file__))

# 해상도 / 레이아웃
WARP_W = 1200
WARP_H = 620
LAYOUT_FILE = os.path.join(current_dir, "key_layout.json")

# 모델 경로
YOLO_PATH = os.path.join(current_dir, "model", "indexFinger_best.pt")
CLASSIFIER_PATH = os.path.join(current_dir, "model", "touch_classifier_best.pth")

# 터치 인식 관련 파라미터
COOLDOWN_TIME = 0.2
TOUCH_MIN_DURATION = 0.1

# 키 매핑
SPECIAL_KEYS = {
    "SpaceBar": "space", "Enter": "enter", "Backspace": "backspace",
    "Tab": "tab", "CapsRock": "capslock", "Shift": "shift",
    "RShift": "shiftright", "Ctrl": "ctrl", "Win": "win",
    "Alt": "alt", "up": "up", "down": "down",
    "left": "left", "right": "right", "~": "`"
}

# 디바이스
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
