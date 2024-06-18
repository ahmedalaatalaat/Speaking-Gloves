from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async
from ultralytics import YOLO
from .models import *
import numpy as np
import base64
import json
import cv2

model = YOLO('live_detect/ai_model/best.pt')

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("welcome" * 100)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Process received frames
            np_arr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Perform YOLO inference
            results = model(frame)
            processed_data = []

            # Process the results and draw bounding boxes
            for result in results[0].boxes.data.tolist():
                x1, y1, x2, y2, conf, cls = result
                processed_data.append({
                    'class': model.names[int(cls)],
                    'confidence': conf,
                    'box': [x1, y1, x2, y2]
                })

                # Draw bounding box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f"{model.names[int(cls)]}: {conf:.2f}"
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Encode frame back to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Save the image to the database
            await sync_to_async(self.save_image_to_db)(frame_bytes)

            # Send the frame with bounding boxes back to the client
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            await self.send(text_data=json.dumps({
                'image': frame_base64,
                'detections': processed_data
            }))
            
        
    def save_image_to_db(self, frame_bytes):
        annotated_image = AnnotatedImage()
        annotated_image.image.save('annotated_image.jpg', ContentFile(frame_bytes))
        annotated_image.save()

