import cv2
import numpy as np
from ultralytics import YOLO
import serial
import re
import requests

# ====== SETUP YOLO & STEREO CAMERA ======
model = YOLO("yolov8n.pt")

cv_file = cv2.FileStorage("stereo_calibration.xml", cv2.FILE_STORAGE_READ)
mtxL = cv_file.getNode("mtxL").mat()
distL = cv_file.getNode("distL").mat()
mtxR = cv_file.getNode("mtxR").mat()
distR = cv_file.getNode("distR").mat()
R = cv_file.getNode("R").mat()
T = cv_file.getNode("T").mat()
cv_file.release()

capL = cv2.VideoCapture(2)
capR = cv2.VideoCapture(3)

retL, frameL = capL.read()
h, w = frameL.shape[:2]

R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(mtxL, distL, mtxR, distR, (w, h), R, T)
mapLx, mapLy = cv2.initUndistortRectifyMap(mtxL, distL, R1, P1, (w, h), cv2.CV_32FC1)
mapRx, mapRy = cv2.initUndistortRectifyMap(mtxR, distR, R2, P2, (w, h), cv2.CV_32FC1)

baseline = np.linalg.norm(T)
focal_length = P1[0, 0]

stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=16 * 6,
    blockSize=5,
    P1=8 * 3 * 5 ** 2,
    P2=32 * 3 * 5 ** 2,
    mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
)

# ====== SETUP GPS & REM ======
gps_serial = serial.Serial('COM3', 9600, timeout=1)  # Ganti COM sesuai port Arduino
ESP32_IP = "http://192.168.1.50"  # Ganti dengan IP ESP32

def rem():
    try:
        requests.get(f"{ESP32_IP}/rem_on", timeout=1)
        print("[ESP32] Rem AKTIF")
    except:
        print("[ESP32] Gagal kirim perintah rem")

def jalan():
    try:
        requests.get(f"{ESP32_IP}/rem_off", timeout=1)
        print("[ESP32] Rem NONAKTIF")
    except:
        print("[ESP32] Gagal kirim perintah jalan")

def get_gps():
    while True:
        line = gps_serial.readline().decode('utf-8', errors='ignore').strip()
        match = re.search(r"LAT:([-\d.]+),LON:([-\d.]+)", line)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            print(f"[GPS] {lat}, {lon}")
            return lat, lon

def kirim_koordinat(lat, lon):
    try:
        requests.post("https://yourcloud.com/upload_gps", json={"lat": lat, "lon": lon}, timeout=2)
        print("[Cloud] Koordinat terkirim")
    except:
        print("[Cloud] Gagal kirim koordinat")

# ====== MAIN LOOP ======
while True:
    retL, frameL = capL.read()
    retR, frameR = capR.read()
    if not retL or not retR:
        break

    rectL = cv2.remap(frameL, mapLx, mapLy, cv2.INTER_LINEAR)
    rectR = cv2.remap(frameR, mapRx, mapRy, cv2.INTER_LINEAR)
    grayL = cv2.cvtColor(rectL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(rectR, cv2.COLOR_BGR2GRAY)
    disparity = stereo.compute(grayL, grayR).astype(np.float32) / 16.0

    results = model(rectL)[0]
    rem_triggered = False

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        if 0 <= cx < w and 0 <= cy < h:
            disp = disparity[cy, cx]
            distance = (focal_length * baseline) / disp if disp > 0 else -1
        else:
            distance = -1

        if label in ["person", "dog", "cat", "car"] and 0 < distance < 2:
            rem()
            if not rem_triggered:
                lat, lon = get_gps()
                kirim_koordinat(lat, lon)
                rem_triggered = True
        else:
            jalan()

        # Visual
        cv2.rectangle(rectL, (x1, y1), (x2, y2), (0, 255, 0), 2)
        text = f"{label} {distance:.2f} m" if distance > 0 else f"{label} ? m"
        cv2.putText(rectL, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
    disp_vis = np.uint8(disp_vis)
    disp_vis = cv2.applyColorMap(disp_vis, cv2.COLORMAP_JET)

    cv2.imshow("Disparity Map", disp_vis)
    cv2.imshow("YOLOv8 + Jarak", rectL)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

capL.release()
capR.release()
cv2.destroyAllWindows()