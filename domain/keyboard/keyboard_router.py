# domain/keyboard/keyboard_router.py
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from .keyboard_service import run_keyboard_session
import cv2

router = APIRouter(
    prefix="/api/keyboard",
    tags=["keyboard"],
)

@router.post("/start")
def start_keyboard(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_keyboard_session)
    return {"status": "started"}

def generate_webcam_stream():
    """
    MJPEG 형식으로 웹캠 프레임을 계속 보내는 제너레이터.
    지금은 순수 웹캠 화면만 보내고,
    나중에 run_keyboard_session 로직(가상키보드 오버레이)을 이 안으로 옮길 수 있습니다.
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ 웹캠을 열 수 없습니다.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 필요하면 여기에서 YOLO / 키보드 레이아웃 오버레이 처리 가능
        # frame = process_frame(frame)

        # JPEG 인코딩
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # MJPEG 형식으로 전송
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

    cap.release()


@router.get("/stream")
def webcam_stream():
    """
    브라우저에서 <img src="/api/keyboard/stream"> 로 접근하는 엔드포인트
    """
    return StreamingResponse(
        generate_webcam_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )