import cv2
import numpy as np
from ultralytics import YOLO
from norfair import Detection, Tracker
import os
import datetime
import csv
import threading
import requests
from aiohttp import web
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from av import VideoFrame

model = YOLO("bismillah2.pt")
tracker = Tracker(distance_function="euclidean", distance_threshold=30)

current_frame = None
lock = threading.Lock()

cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

os.makedirs("capture_anomali", exist_ok=True)
csv_path = "capture_anomali/koordinat_anomali.csv"
if not os.path.exists(csv_path):
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "filename", "x1", "y1", "x2", "y2", "class_id"])

intruder_present = False
last_lat, last_lon = None, None

def get_centroid_from_box(box):
    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return np.array([[cx.item(), cy.item()]])

def point_in_trapezoid(pt, polygon):
    return cv2.pointPolygonTest(polygon, (int(pt[0][0]), int(pt[0][1])), False) >= 0

def detection_loop():
    global current_frame, intruder_present, last_lat, last_lon
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        height, width = frame.shape[:2]
        frame_overlay = frame.copy()

        # Trapezoid ROI
        trapezoid_pts = np.array([
            [int(width * 0.0), height],
            [int(width * 1.0), height],
            [int(width * 1.0), int(height * 1)],
            [int(width * 0.0), int(height * 1)]
        ], np.int32)
        cv2.polylines(frame_overlay, [trapezoid_pts], isClosed=True, color=(0, 255, 255), thickness=2)
        trapezoid_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(trapezoid_mask, [trapezoid_pts], 255)

        results = model.predict(frame, conf=0.2, stream=False, verbose=False)[0]
        detections = []
        masks = []
        intruder_detected = False
        captured_box = None
        captured_cls = None

        if results.boxes is not None and results.masks is not None:
            boxes = results.boxes.xyxy
            class_ids = results.boxes.cls.cpu().numpy().astype(int)
            masks_all = results.masks.data.cpu().numpy()

            for i, (box, mask, cls_id) in enumerate(zip(boxes, masks_all, class_ids)):
                centroid = get_centroid_from_box(box)
                if not point_in_trapezoid(centroid, trapezoid_pts):
                    continue
                # Segmentasi dan bounding box untuk semua objek
                mask_uint8 = (mask * 255).astype(np.uint8)
                mask_clipped = cv2.bitwise_and(mask_uint8, trapezoid_mask)
                colored_mask = cv2.merge([mask_clipped, np.zeros_like(mask_clipped), np.zeros_like(mask_clipped)])
                frame_overlay = cv2.addWeighted(frame_overlay, 1, colored_mask, 0.4, 0)
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame_overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame_overlay, f"Anomali", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                if cls_id not in [1, 2]:
                    intruder_detected = True
                    detections.append(Detection(points=centroid))
                    # Simpan box dan class untuk CSV jika capture
                    if captured_box is None:
                        captured_box = (x1, y1, x2, y2)
                        captured_cls = cls_id

        # Capture frame jika intruder baru masuk (transisi False -> True)
        if intruder_detected and not intruder_present and captured_box is not None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            img_name = f"anomali_{timestamp}.jpg"
            img_path = os.path.join("capture_anomali", img_name)
            cv2.imwrite(img_path, frame_overlay)
            # Simpan ke CSV
            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                x1, y1, x2, y2 = captured_box
                writer.writerow([timestamp, img_name, x1, y1, x2, y2, captured_cls])
        intruder_present = intruder_detected

        # Update Norfair Tracker
        tracked_objects = tracker.update(detections=detections)

        # Encode ke JPEG untuk streaming
        _, jpeg = cv2.imencode('.jpg', frame_overlay)
        with lock:
            current_frame = jpeg.tobytes()

        cv2.waitKey(1)

threading.Thread(target=detection_loop, daemon=True).start()

def get_latest_anomali_frame():
    with lock:
        return current_frame

class AnomaliStreamTrack(VideoStreamTrack):
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame_bytes = get_latest_anomali_frame()
        if frame_bytes is not None:
            frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

async def offer_anomali(request):
    try:
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        pc = RTCPeerConnection()
        pc.addTrack(AnomaliStreamTrack())
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        return web.json_response({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

app = web.Application()
app.router.add_post("/offer_anomali", offer_anomali)

if __name__ == "__main__":
    web.run_app(app, port=8082)
