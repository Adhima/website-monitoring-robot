from flask import Flask, Response
import cv2

app = Flask(__name__)
cap = cv2.VideoCapture(1)

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h2>Streaming Webcam via Flask</h2><img src="/video" width="640">'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)