import cv2
import time
import numpy as np
from pathlib import Path
from typing import Generator, List, Optional
from backend.config import SAMPLES_DIR

class FactoryCameraSimulator:
    def __init__(self):
        self.image_paths: List[Path] = list(SAMPLES_DIR.glob('*.jpg'))
        self.current_idx = 0
        self.offset_x = 0
        self.is_running = True

    def get_frame(self) -> np.ndarray:
        if not self.image_paths:
            # Fallback black frame if no images
            frame = np.zeros((300, 800, 3), dtype=np.uint8)
            cv2.putText(frame, "NO CAMERA FEED", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame

        path = self.image_paths[self.current_idx]
        img = cv2.imread(str(path))
        if img is None:
            img = np.zeros((256, 1600, 3), dtype=np.uint8)

        h, w = img.shape[:2]
        crop_w = min(800, w)
        crop_h = min(256, h)

        # Pan across steel sheet like a rolling conveyor
        self.offset_x = (self.offset_x + 12) % max(1, w - crop_w)
        if self.offset_x < 12:
            self.current_idx = (self.current_idx + 1) % len(self.image_paths)

        crop = img[0:crop_h, self.offset_x:self.offset_x + crop_w].copy()

        # Telemetry HUD
        hud = cv2.resize(crop, (900, 320))
        h_hud, w_hud = hud.shape[:2]

        # Draw scanning laser line
        laser_x = int((time.time() * 250) % w_hud)
        cv2.line(hud, (laser_x, 0), (laser_x, h_hud), (0, 255, 255), 2)
        cv2.line(hud, (laser_x - 3, 0), (laser_x - 3, h_hud), (0, 200, 255), 1)

        # Top banner overlay
        cv2.rectangle(hud, (0, 0), (w_hud, 35), (15, 20, 28), -1)
        cv2.putText(hud, "LIVE FACTORY STREAM: LINE #4 - FEEDSTOCK VI QUALITY SCANNER", (15, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 200), 2)

        # Bottom status
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        status_text = f"CONVEYOR: 1.2 m/s | FPS: 24.8 | ROLL: {path.stem} | {ts}"
        cv2.rectangle(hud, (0, h_hud - 28), (w_hud, h_hud), (15, 20, 28), -1)
        cv2.putText(hud, status_text, (15, h_hud - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        return hud

    def generate_mjpeg_stream(self) -> Generator[bytes, None, None]:
        while self.is_running:
            frame = self.get_frame()
            ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ret:
                frame_bytes = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.04)  # ~25 FPS

_simulator: Optional[FactoryCameraSimulator] = None

def get_camera_simulator() -> FactoryCameraSimulator:
    global _simulator
    if _simulator is None:
        _simulator = FactoryCameraSimulator()
    return _simulator
