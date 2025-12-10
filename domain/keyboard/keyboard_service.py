# domain/keyboard/keyboard_service.py
import cv2
from .keyboard_model import load_models
from .keyboard_layout import (
    load_key_layout,
    create_empty_keyboard_view,
    draw_keyboard_layout,
)
from .keyboard_aruco import ArucoTracker
from .keyboard_finger import FingerTracker


def run_keyboard_session():
    """
    FastAPI BackgroundTasks에서 호출할 메인 루프
    - 웹캠 열기
    - Aruco + 손가락 추적
    - cv2 윈도우 두 개 표시
    """
    yolo_model, touch_model, transform = load_models()
    key_layout = load_key_layout()

    aruco_tracker = ArucoTracker()
    finger_tracker = FingerTracker(yolo_model, touch_model, transform, key_layout)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 웹캠을 열 수 없습니다.")
        return

    print("=== AI 터치 키보드 (시각화 포함) 시작 ===")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            matrix = aruco_tracker.update(frame)

            warped_view = create_empty_keyboard_view()
            draw_keyboard_layout(warped_view, key_layout)

            frame, warped_view = finger_tracker.process(frame, matrix, warped_view)

            cv2.imshow("Tracking Cam", frame)
            cv2.imshow("AI Keyboard", warped_view)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
