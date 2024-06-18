from contextlib import contextmanager
from ultralytics import YOLO
import threading
import cv2
import numpy as np
import imageio.v3 as iio

model = YOLO('live_detect/ai_model/best.pt')

class VideoCamera:
    def __init__(self):
        self.lock = threading.Lock()
        self.frame = None
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def release(self):
        if self.thread.is_alive():
            self.thread.join()

    def update(self):
        reader = iio.get_reader("<video0>", plugin="ffmpeg")
        for frame in reader:
            with self.lock:
                self.frame = frame
            # Break the loop if the thread should stop
            if not self.thread.is_alive():
                break

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None

            # Perform inference
            results = model(self.frame)

            # Process results
            for result in results[0].boxes.data.tolist():
                x1, y1, x2, y2, conf, cls = result

                # Draw the box and label on the frame
                frame = np.array(self.frame)
                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f'{model.names[int(cls)]}: {conf:.2f}'
                frame = cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()

camera = VideoCamera()

def gen_frames2():
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    