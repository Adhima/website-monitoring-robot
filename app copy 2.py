from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from flask_socketio import SocketIO, emit
from flask_mysqldb import MySQL
import MySQLdb.cursors
import cv2
import time
from ultralytics import YOLO
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Konfigurasi MySQL di Laragon
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Sesuaikan dengan user MySQL Anda
app.config['MYSQL_PASSWORD'] = 'thedhimma7'  # Sesuaikan dengan password MySQL Anda
app.config['MYSQL_DB'] = 'flask_login'  # Sesuaikan dengan nama database Anda

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')  # Menghindari error KeyError
    password = request.form.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    account = cursor.fetchone()

    if account:
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Username atau password salah!", username=username)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session["username"])
    return redirect(url_for('home'))

socketio = SocketIO(app, cors_allowed_origins="*")

# Load Model YOLOv8 untuk deteksi mobil dan manusia
model_mobil = YOLO("yolov8n.pt")   # Model untuk deteksi mobil
model_manusia = YOLO("yolov8n.pt") # Model untuk deteksi manusia

# RTSP URL untuk IP Camera (Ganti sesuai kamera Anda)

# Variabel untuk menyimpan FPS masing-masing kamera
fps_mobil = 0
fps_manusia = 0

# Status Kamera
camera_status = {"ipcam": True, "webcam": True}


def stream_mobil():
    """ Fungsi untuk streaming deteksi mobil dari IP Camera """
    global fps_mobil, camera_status
    cap = cv2.VideoCapture(2) 

    if not cap.isOpened():
        print("Error: Tidak dapat membuka IP Camera")
        camera_status["ipcam"] = False
        socketio.emit("camera_status", {"type": "ipcam", "status": "notfound"})
        return

    camera_status["ipcam"] = True
    socketio.emit("camera_status", {"type": "ipcam", "status": "active"})

    prev_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Deteksi objek dengan YOLOv8
        results = model_mobil(frame)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])  
                conf = box.conf[0]  
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Hanya tampilkan jika objek adalah mobil (coco ID mobil = 2, 3, 5, 7)
                if cls_id in [2, 3, 5, 7]:  
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"Mobil {conf:.2f}", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Hitung FPS
        curr_time = time.time()
        fps_mobil = round(1 / (curr_time - prev_time), 2)
        prev_time = curr_time

        socketio.emit("update_fps", {"type": "ipcam", "fps": fps_mobil})

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()


def stream_manusia():
    """ Fungsi untuk streaming deteksi manusia dari Webcam Laptop """
    global fps_manusia, camera_status
    cap = cv2.VideoCapture(1)  # 0 untuk webcam internal

    if not cap.isOpened():
        print("Error: Tidak dapat membuka Webcam")
        camera_status["webcam"] = False
        socketio.emit("camera_status", {"type": "webcam", "status": "notfound"})
        return

    camera_status["webcam"] = True
    socketio.emit("camera_status", {"type": "webcam", "status": "active"})

    prev_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Deteksi manusia dengan YOLOv8
        results = model_manusia(frame)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])  
                conf = box.conf[0]  
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Hanya tampilkan jika objek adalah manusia (coco ID manusia = 0)
                if cls_id == 0:  
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f"Manusia {conf:.2f}", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Hitung FPS
        curr_time = time.time()
        fps_manusia = round(1 / (curr_time - prev_time), 2)
        prev_time = curr_time

        socketio.emit("update_fps", {"type": "webcam", "fps": fps_manusia})

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/data')
def data():
    if 'loggedin' not in session:
        return redirect(url_for('home'))

    kategori_data = {
        'anomali': [],
        'penambat': [],
        'bantalan': [],
        'kemiringan': []
    }

    # Contoh dummy data bisa ditambahkan di sini jika diperlukan

    return render_template("data.html", kategori_data=kategori_data)

@app.route('/video_feed/ipcam')
def video_feed_ipcam():
    return Response(stream_mobil(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/video_feed/webcam')
def video_feed_webcam():
    return Response(stream_manusia(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/get_fps/ipcam')
def get_fps_ipcam():
    return jsonify({"fps": fps_mobil})


@app.route('/get_fps/webcam')
def get_fps_webcam():
    return jsonify({"fps": fps_manusia})

@app.route("/speed", methods=["POST"])
def receive_speed():
    data = request.json
    speed = data.get("speed", 0)
    socketio.emit("speed_update", {"speed": speed})
    return jsonify({"status": "ok"})

# Lampu status disimpan global
lamp_status = False

@app.route('/lamp', methods=['POST'])
def lamp_control():
    global lamp_status
    data = request.get_json()
    lamp_status = data.get("lamp", False)
    print(f"[FLASK] Lampu: {'ON' if lamp_status else 'OFF'}")
    return jsonify({"status": "ok"})

@app.route('/lamp_status', methods=['GET'])
def lamp_status_api():
    return jsonify({"lamp": lamp_status})

# Motor status disimpan global
motor_status = False
motor_speed = 0  # dalam km/h

@app.route('/motor', methods=['POST'])
def motor_control():
    global motor_status, motor_speed
    data = request.get_json()
    motor_status = data.get("motor", False)

    if not motor_status:
        motor_speed = 0  # reset speed saat motor dimatikan

    return jsonify({"status": "ok"})

@app.route('/motor_status', methods=['GET'])
def motor_status_api():
    return jsonify({"motor": motor_status})

# Kecepatan target motor disimpan global

@app.route("/motor_speed", methods=["POST"])
def motor_speed():
    global motor_target_speed
    data = request.get_json()
    motor_target_speed = data.get("speed", 0)
    print(f"[FLASK] Target Speed: {motor_target_speed} km/h")
    return jsonify({"status": "ok"})

@app.route("/motor_speed_status", methods=["GET"])
def motor_speed_status():
    return jsonify({"speed": motor_target_speed})


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
