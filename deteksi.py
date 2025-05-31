# deteksi.py
import cv2, asyncio
import numpy as np
from aiohttp import web
from ultralytics import YOLO
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from av import VideoFrame
import aiohttp_cors
import os
import datetime
import threading

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

os.makedirs("capture_human", exist_ok=True)
last_detected = False
latest_frame = np.zeros((480, 640, 3), dtype=np.uint8)
lock = threading.Lock()

def detection_loop():
    global last_detected, latest_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        results = model(frame, verbose=False)[0]

        detected = False
        for box in results.boxes:
            cls = int(box.cls[0])
            if cls == 0:
                detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Human", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Capture hanya saat transisi dari tidak terdeteksi ke terdeteksi
        if detected and not last_detected:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_human/human_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
        last_detected = detected

        with lock:
            latest_frame = frame.copy()

# Jalankan deteksi di background
threading.Thread(target=detection_loop, daemon=True).start()

class HumanStreamTrack(VideoStreamTrack):
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        with lock:
            frame = latest_frame.copy()
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

async def offer(request):
    print("Received WebRTC offer")
    try:
        params = await request.json()
        print("params:", params)
        if not params.get("sdp") or not params.get("type"):
            return web.json_response({"error": "Missing sdp or type"}, status=400)
        if params["type"] not in ["offer", "answer", "pranswer", "rollback"]:
            return web.json_response({"error": "Invalid type"}, status=400)
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        pc = RTCPeerConnection()
        pc.addTrack(HumanStreamTrack())
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    except Exception as e:
        print("Error in offer:", e)
        return web.json_response({"error": str(e)}, status=500)

app = web.Application()
app.router.add_post("/offer", offer)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == "__main__":
    web.run_app(app, port=8080)
