from flask import Flask, Response
import cv2
from ultralytics import YOLO
import threading

app = Flask(__name__)

# Load model dan set class ID target
model = YOLO("yolov8n.pt")
targets = {
    "orang": {"camera_index": 0, "class_ids": [0]},   # class_id 0 = person
    "mobil": {"camera_index": 1, "class_ids": [2]},   # class_id 2 = car
    "botol": {"camera_index": 2, "class_ids": [39]}   # class_id 39 = bottle
}

# Global untuk menyimpan frame hasil deteksi
output_frames = {
    "orang": None,
    "mobil": None,
    "botol": None
}

def detect_objects(name):
    cap = cv2.VideoCapture(targets[name]["camera_index"])
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        results = model(frame, stream=True, verbose=False)
        for r in results:
            for box, cls in zip(r.boxes.xyxy, r.boxes.cls):
                if int(cls) in targets[name]["class_ids"]:
                    x1, y1, x2, y2 = map(int, box)
                    label = model.names[int(cls)]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        _, buffer = cv2.imencode('.jpg', frame)
        output_frames[name] = buffer.tobytes()

# Start thread untuk masing-masing deteksi
for key in targets:
    t = threading.Thread(target=detect_objects, args=(key,))
    t.daemon = True
    t.start()

# Route video untuk masing-masing objek
@app.route('/video/<kategori>')
def video_feed(kategori):
    def generate():
        while True:
            frame = output_frames.get(kategori)
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
