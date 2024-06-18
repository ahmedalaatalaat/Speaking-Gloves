from contextlib import contextmanager
from ultralytics import YOLO
import threading
import cv2

model = YOLO('live_detect/ai_model/best.pt')


# class VideoCamera2(object):
#     def __init__(self) -> None:
#         self.video = cv2.VideoCapture(0)
#         (self.grabbed, self.frame) = self.video.read()
#         threading.Thread(target=self.update, args=()).start()
        
    
#     def __del__(self):
#         self.video.release()
        
#     def get_frame(self):
#         image = self.frame
#         _, jpeg = cv2.imencode('.jpg', image)
#         return jpeg.tobytes()
    
#     def update(self):
#         while True:
#             (self.grabbed, self.frame) = self.video.read()
            

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


class VideoCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(cv2.CAP_V4L2)
        self.frame = None
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update, args=())
        self.counter = 0  # Initialize the counter
        self.thread.daemon = True
        self.thread.start()

    def __del__(self):
        self.cap.release()

    def update(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Resize frame for faster processing
            frame = cv2.resize(frame, (640, 480))

            with self.lock:
                self.frame = frame

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            
            self.counter += 1
            if self.counter % 3 != 0:
                # Skip processing for this frame
                return None
            
            # Perform inference
            results = model(self.frame)

            # Process results
            for result in results[0].boxes.data.tolist():
                x1, y1, x2, y2, conf, cls = result

                # Draw the box and label on the frame
                cv2.rectangle(self.frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f'{model.names[int(cls)]}: {conf:.2f}'
                cv2.putText(self.frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', self.frame)
            return buffer.tobytes()


# @contextmanager
# def get_video_camera():
#     camera = VideoCamera()
#     try:
#         yield camera
#     finally:
#         camera.release()


def gen_frames(camera):
    # camera = VideoCamera()
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # cap.release()
    # cv2.destroyAllWindows()

# def generate_frames():
#     cap = cv2.VideoCapture(0)  # Open webcam
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Perform inference
#         results = model(frame)

#         # Process results
#         for result in results[0].boxes.data.tolist():
#             x1, y1, x2, y2, conf, cls = result

#             # Draw the box and label on the frame
#             cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
#             label = f'{model.names[int(cls)]}: {conf:.2f}'
#             cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         # Encode the frame in JPEG format
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#     cap.release()

