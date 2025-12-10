# domain/keyboard/keyboard_finger.py
import time
import cv2
import numpy as np
from PIL import Image
import pyautogui
import torch
from .keyboard_config import (
    COOLDOWN_TIME,
    TOUCH_MIN_DURATION,
    WARP_W,
    WARP_H,
    SPECIAL_KEYS,
    DEVICE,
)

class FingerTracker:
    def __init__(self, yolo_model, touch_model, transform, key_layout):
        self.yolo_model = yolo_model
        self.touch_model = touch_model
        self.transform = transform
        self.key_layout = key_layout
        self.fingers_state = {}

    def process(self, frame, matrix, warped_view):
        """
        한 프레임에 대해:
        - YOLO 추적
        - 터치 여부 분류
        - 키보드 좌표 변환
        - pyautogui.press 호출
        - frame / warped_view 위에 시각화
        """
        results = self.yolo_model.track(
            frame, persist=True, verbose=False, device=DEVICE
        )

        curr_time = time.time()
        current_ids = set()

        for r in results:
            if r.boxes.id is None:
                continue

            boxes = r.boxes.xyxy.cpu().numpy()
            track_ids = r.boxes.id.int().cpu().numpy()

            for box, track_id in zip(boxes, track_ids):
                current_ids.add(track_id)

                if track_id not in self.fingers_state:
                    self.fingers_state[track_id] = {
                        "last_input": 0,
                        "is_touching": False,
                        "touch_start_time": 0,
                    }
                st = self.fingers_state[track_id]

                x1, y1, x2, y2 = map(int, box)
                h, w, _ = frame.shape
                cx1, cy1 = max(0, x1), max(0, y1)
                cx2, cy2 = min(w, x2), min(h, y2)
                finger_img = frame[cy1:cy2, cx1:cx2]

                # 터치/호버 분류
                is_touch_visual = False
                if finger_img.size > 0:
                    pil_img = Image.fromarray(
                        cv2.cvtColor(finger_img, cv2.COLOR_BGR2RGB)
                    )
                    input_tensor = self.transform(pil_img).unsqueeze(0).to(DEVICE)
                    with torch.no_grad():
                        output = self.touch_model(input_tensor)
                        prob = torch.softmax(output, dim=1)
                        is_touch_visual = prob[0][1].item() > 0.5

                fx, fy = (x1 + x2) / 2, (y1 - y2) / 3 + y2
                color = (0, 255, 255) if is_touch_visual else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                status_text = "TOUCH" if is_touch_visual else "HOVER"
                cv2.putText(
                    frame,
                    status_text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

                if matrix is not None:
                    pts = np.array([[[fx, fy]]], dtype=np.float32)
                    trans = cv2.perspectiveTransform(pts, matrix)
                    tx, ty = trans[0][0]

                    if 0 <= tx < WARP_W and 0 <= ty < WARP_H:
                        cv2.circle(
                            warped_view, (int(tx), int(ty)), 8, (0, 0, 255), -1
                        )

                        detected_key = None
                        for key_name, rect in self.key_layout.items():
                            rx, ry, rw, rh = (
                                rect["x"],
                                rect["y"],
                                rect["w"],
                                rect["h"],
                            )
                            if rx < tx < rx + rw and ry < ty < ry + rh:
                                detected_key = key_name
                                break

                        if detected_key and is_touch_visual:
                            if st["touch_start_time"] == 0:
                                st["touch_start_time"] = curr_time

                            duration = curr_time - st["touch_start_time"]
                            if (
                                duration >= TOUCH_MIN_DURATION
                                and not st["is_touching"]
                                and curr_time - st["last_input"] > COOLDOWN_TIME
                            ):
                                print(f"👉 Input({track_id}): {detected_key}")

                                py_key = SPECIAL_KEYS.get(
                                    detected_key, detected_key.lower()
                                )
                                if py_key:
                                    pyautogui.press(py_key)

                                st["last_input"] = curr_time
                                st["is_touching"] = True

                                rx, ry, rw, rh = (
                                    self.key_layout[detected_key]["x"],
                                    self.key_layout[detected_key]["y"],
                                    self.key_layout[detected_key]["w"],
                                    self.key_layout[detected_key]["h"],
                                )
                                cv2.rectangle(
                                    warped_view,
                                    (rx, ry),
                                    (rx + rw, ry + rh),
                                    (0, 0, 255),
                                    -1,
                                )
                        else:
                            st["touch_start_time"] = 0
                            st["is_touching"] = False

        # 사라진 손가락 track_id 정리
        expired_ids = [
            k for k in self.fingers_state.keys() if k not in current_ids
        ]
        for k in expired_ids:
            del self.fingers_state[k]

        return frame, warped_view
