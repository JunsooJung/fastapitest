# domain/keyboard/keyboard_models.py
import torch
import torch.nn as nn
from torchvision import transforms
from ultralytics import YOLO
from .keyboard_config import YOLO_PATH, CLASSIFIER_PATH, DEVICE

class TouchClassifier(nn.Module):
    def __init__(self):
        super(TouchClassifier, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(128 * 8 * 8, 256), nn.ReLU(),
            nn.Dropout(0.5), nn.Linear(256, 2)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def load_models():
    """YOLO + 터치 분류 모델 로드"""
    print(f"🚀 디바이스: {DEVICE}")

    yolo_model = YOLO(YOLO_PATH)

    touch_model = TouchClassifier().to(DEVICE)
    touch_model.load_state_dict(torch.load(CLASSIFIER_PATH, map_location=DEVICE))
    touch_model.eval()

    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor()
    ])

    return yolo_model, touch_model, transform
