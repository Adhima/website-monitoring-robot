import cv2
import threading
import cv2
import numpy as np
from ultralytics import YOLO
from norfair import Detection, Tracker

latest_frame_rectL = None
lock = threading.Lock()

# === Load YOLOv8 model ===
model = YOLO("bismillah2.pt")  # Ganti dengan modelmu

# === Load kalibrasi stereo ===
cv_file = cv2.FileStorage("stereo_calibration.xml", cv2.FILE_STORAGE_READ)
mtxL = cv_file.getNode("mtxL").mat()
distL = cv_file.getNode("distL").mat()
mtxR = cv_file.getNode("mtxR").mat()
distR = cv_file.getNode("distR").mat()
R = cv_file.getNode("R").mat()
T = cv_file.getNode("T").mat()
cv_file.release()

# === Kamera stereo ===
capL = cv2.VideoCapture(0)
capR = cv2.VideoCapture(3)

retL, frameL = capL.read()
h, w = frameL.shape[:2]

R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(mtxL, distL, mtxR, distR, (w, h), R, T)
mapLx, mapLy = cv2.initUndistortRectifyMap(mtxL, distL, R1, P1, (w, h), cv2.CV_32FC1)
mapRx, mapRy = cv2.initUndistortRectifyMap(mtxR, distR, R2, P2, (w, h), cv2.CV_32FC1)

baseline = np.linalg.norm(T)
focal_length = P1[0, 0]

# === Stereo matcher ===
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=64,        # harus kelipatan 16
    blockSize=21,             # semakin besar = lebih halus tapi lebih berat
    P1=8 * 3 * 5 ** 2,
    P2=32 * 3 * 5 ** 2,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=64,
    mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
)

'''
stereo = cv2.StereoSGBM_create(
    minDisparity=0, numDisparities=64, blockSize=21,
    P1=8 * 3 * 5**2, P2=32 * 3 * 5**2,
    disp12MaxDiff=1, uniquenessRatio=10,
    speckleWindowSize=100, speckleRange=64,
    mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
)
'''

# === Norfair tracker ===
tracker = Tracker(distance_function="euclidean", distance_threshold=30)

def get_centroid(box):
    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return np.array([[cx.item(), cy.item()]])

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

    height, width = rectL.shape[:2]
    trapezoid_pts = np.array([
        [int(width * 0.05), height],
        [int(width * 0.95), height],
        [int(width * 0.65), int(height * 0.6)],
        [int(width * 0.35), int(height * 0.6)]
    ], np.int32)
    trapezoid_mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(trapezoid_mask, [trapezoid_pts], 255)

    # ==== YOLOv8 Predict ====
    results = model(rectL, stream=False)[0]
    detections = []
    combined_mask = np.zeros_like(grayL)

    if results.boxes is not None:
        boxes = results.boxes.xyxy
        class_ids = results.boxes.cls.cpu().numpy().astype(int)

        for i, (box, cls_id) in enumerate(zip(boxes, class_ids)):
            x1, y1, x2, y2 = box
            centroid = get_centroid(box)

            # Skip kalau centroid di luar trapezoid
            if cv2.pointPolygonTest(trapezoid_pts, (int(centroid[0][0]), int(centroid[0][1])), False) < 0:
                continue

            # Tambahkan ke tracking Norfair
            detections.append(Detection(points=centroid))

            # Estimasi jarak via disparity
            x1i, y1i, x2i, y2i = int(x1), int(y1), int(x2), int(y2)
            disp_roi = disparity[y1i:y2i, x1i:x2i]
            valid_disp = disp_roi[disp_roi > 0]

            if valid_disp.size > 0:
                disparity_value = np.median(valid_disp)
                distance = (focal_length * baseline) / disparity_value
            else:
                distance = -1  # tampilkan tanda ?
            
            '''
            cx, cy = int(centroid[0][0]), int(centroid[0][1])
            disp = disparity[cy, cx] if 0 <= cx < width and 0 <= cy < height else -1
            distance = (focal_length * baseline / disp) if disp > 0 else -1
            '''

            label = model.names[cls_id]
            cv2.rectangle(rectL, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            text = f"{label} {distance:.2f} m" if distance > 0 else f"{label} ? m"
            cv2.putText(rectL, text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # ==== Segmentasi Mask ====
    if results.masks is not None:
        for mask in results.masks.data.cpu().numpy():
            mask_uint8 = (mask * 255).astype(np.uint8)
            clipped = cv2.bitwise_and(mask_uint8, trapezoid_mask)
            combined_mask = cv2.bitwise_or(combined_mask, clipped)
            color_mask = cv2.merge([clipped, np.zeros_like(clipped), np.zeros_like(clipped)])
            rectL = cv2.addWeighted(rectL, 1, color_mask, 0.4, 0)

    # ==== Norfair Tracking ====
    tracked_objects = tracker.update(detections=detections)
    for obj in tracked_objects:
        x, y = obj.estimate[0]
        #cv2.circle(rectL, (int(x), int(y)), 5, (0, 255, 0), -1)
        # (tidak menampilkan ID)

    # ==== Canny + Highlight ====
    edges = cv2.Canny(grayL, 50, 150)
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    edges_bgr[np.where((combined_mask == 255) & (edges == 255))] = [0, 0, 255]
    edges_bgr[np.where((combined_mask == 0) & (edges == 255))] = [255, 255, 255]
    cv2.polylines(edges_bgr, [trapezoid_pts], isClosed=True, color=(0, 255, 255), thickness=1)

    # ==== Tampilkan ====
    #cv2.imshow("Kamera Kiri (Tracking + Segmentasi + Jarak)", rectL)
    #cv2.imshow("Kamera Kanan", rectR)
    #cv2.imshow("Canny Edge (Highlight Area)", edges_bgr)

    #if cv2.waitKey(1) & 0xFF == 27:  # ESC
    #    break
ret, jpeg = cv2.imencode('.jpg', rectL)
if ret:
    with lock:
        latest_frame_rectL = jpeg.tobytes()

def get_latest_frame_rectL():
    global latest_frame_rectL
    with lock:
        return latest_frame_rectL

'''
capL.release()
capR.release()
cv2.destroyAllWindows()
'''