import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import pyautogui
import math

MONITOR_WIDTH, MONITOR_HEIGHT = pyautogui.size()

filter_length = 8

ray_origins = deque(maxlen=filter_length)
ray_directions = deque(maxlen=filter_length)

calibration_offset_yaw = 0.0
calibration_offset_pitch = 0.0

LANDMARKS = {
    "left": 234,
    "right": 454,
    "top": 10,
    "bottom": 152,
    "front": 1,
}

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def landmark_to_np(landmark, w, h):
    return np.array([
        landmark.x * w,
        landmark.y * h,
        landmark.z * w
    ], dtype=float)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam (index 0)")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame from camera, exiting.")
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0].landmark

        key_points = {}
        for name, idx in LANDMARKS.items():
            pt = landmark_to_np(face_landmarks[idx], w, h)
            key_points[name] = pt

        left   = key_points["left"]
        right  = key_points["right"]
        top    = key_points["top"]
        bottom = key_points["bottom"]
        front  = key_points["front"]

        right_axis = right - left
        right_axis /= np.linalg.norm(right_axis) + 1e-9

        up_axis = top - bottom
        up_axis /= np.linalg.norm(up_axis) + 1e-9

        forward_axis = np.cross(right_axis, up_axis)
        forward_axis /= np.linalg.norm(forward_axis) + 1e-9

        forward_axis = -forward_axis

        center = (left + right + top + bottom + front) / 5.0

        ray_origins.append(center)
        ray_directions.append(forward_axis)

        avg_origin = np.mean(ray_origins, axis=0)
        avg_direction = np.mean(ray_directions, axis=0)
        avg_direction /= np.linalg.norm(avg_direction) + 1e-9

        reference_forward = np.array([0.0, 0.0, -1.0])

        xz_proj = np.array([avg_direction[0], 0.0, avg_direction[2]])
        xz_proj /= np.linalg.norm(xz_proj) + 1e-9
        yaw_rad = math.acos(np.clip(np.dot(reference_forward, xz_proj), -1.0, 1.0))
        if avg_direction[0] < 0:
            yaw_rad = -yaw_rad

        yz_proj = np.array([0.0, avg_direction[1], avg_direction[2]])
        yz_proj /= np.linalg.norm(yz_proj) + 1e-9
        pitch_rad = math.acos(np.clip(np.dot(reference_forward, yz_proj), -1.0, 1.0))
        if avg_direction[1] > 0:
            pitch_rad = -pitch_rad

        yaw_deg = math.degrees(yaw_rad)
        pitch_deg = math.degrees(pitch_rad)

        if yaw_deg < 0:
            yaw_deg = abs(yaw_deg)
        elif yaw_deg < 180:
            yaw_deg = 360 - yaw_deg

        if pitch_deg < 0:
            pitch_deg = 360 + pitch_deg

        yawDegrees = 20.0
        pitchDegrees = 10.0

        yaw_deg += calibration_offset_yaw
        pitch_deg += calibration_offset_pitch

        screen_x = int(((yaw_deg - (180.0 - yawDegrees)) / (2.0 * yawDegrees)) * MONITOR_WIDTH)
        screen_y = int(((180.0 + pitchDegrees - pitch_deg) / (2.0 * pitchDegrees)) * MONITOR_HEIGHT)

        screen_x = max(10, min(screen_x, MONITOR_WIDTH - 10))
        screen_y = max(10, min(screen_y, MONITOR_HEIGHT - 10))

        print(f"Screen position: x={screen_x}, y={screen_y}")

cap.release()