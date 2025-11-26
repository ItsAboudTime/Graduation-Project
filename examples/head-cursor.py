"""
Linux-only demo: control the mouse cursor with head pose.

Requires webcam, OpenCV, and MediaPipe. Press 'q' to quit, 'c' to calibrate.
"""

import sys
import os
import math
from collections import deque

import cv2
import mediapipe as mp
import numpy as np

# Ensure project root is on sys.path so 'cursor' package is importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cursor import create_cursor


def main() -> int:
    if not sys.platform.startswith("linux"):
        print("This demo currently supports Linux only.")
        return 1

    cur = create_cursor()
    minx, miny, maxx, maxy = cur.get_virtual_bounds()
    screen_w = maxx - minx + 1
    screen_h = maxy - miny + 1

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam (index 0)")
        return 2

    # Smoothing window for ray origin/direction
    filt_len = 8
    ray_origins: deque[np.ndarray] = deque(maxlen=filt_len)
    ray_dirs: deque[np.ndarray] = deque(maxlen=filt_len)

    # Calibration offsets (added to computed yaw/pitch)
    calib_yaw = 0.0
    calib_pitch = 0.0

    # Mapping sensitivity (degrees around forward direction)
    yaw_span = 20.0
    pitch_span = 10.0

    # Landmark indices used by the head-track prototype
    LANDMARKS = {
        "left": 234,
        "right": 454,
        "top": 10,
        "bottom": 152,
        "front": 1,
    }

    print("Head-Cursor demo running (Linux). Press 'q' to quit, 'c' to calibrate.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame from camera, exiting.")
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark

            def lmk(i: int) -> np.ndarray:
                p = lm[i]
                return np.array([p.x * w, p.y * h, p.z * w], dtype=float)

            left = lmk(LANDMARKS["left"])   # near left cheek
            right = lmk(LANDMARKS["right"]) # near right cheek
            top = lmk(LANDMARKS["top"])     # near forehead
            bottom = lmk(LANDMARKS["bottom"]) # chin
            front = lmk(LANDMARKS["front"])   # nose tip-ish

            right_axis = right - left
            right_axis /= (np.linalg.norm(right_axis) + 1e-9)

            up_axis = top - bottom
            up_axis /= (np.linalg.norm(up_axis) + 1e-9)

            fwd = np.cross(right_axis, up_axis)
            fwd /= (np.linalg.norm(fwd) + 1e-9)
            fwd = -fwd  # point forward

            center = (left + right + top + bottom + front) / 5.0

            ray_origins.append(center)
            ray_dirs.append(fwd)

            avg_dir = np.mean(ray_dirs, axis=0)
            avg_dir /= (np.linalg.norm(avg_dir) + 1e-9)

            ref_fwd = np.array([0.0, 0.0, -1.0])

            # Yaw: rotation around Y (left/right)
            xz = np.array([avg_dir[0], 0.0, avg_dir[2]])
            xz /= (np.linalg.norm(xz) + 1e-9)
            yaw = math.degrees(math.acos(np.clip(np.dot(ref_fwd, xz), -1.0, 1.0)))
            if avg_dir[0] < 0:
                yaw = -yaw

            # Pitch: rotation around X (up/down)
            yz = np.array([0.0, avg_dir[1], avg_dir[2]])
            yz /= (np.linalg.norm(yz) + 1e-9)
            pitch = math.degrees(math.acos(np.clip(np.dot(ref_fwd, yz), -1.0, 1.0)))
            if avg_dir[1] > 0:
                pitch = -pitch

            # Convert to the 0..360 scheme used by the prototype
            if yaw < 0:
                yaw = abs(yaw)
            elif yaw < 180:
                yaw = 360 - yaw
            if pitch < 0:
                pitch = 360 + pitch

            # Apply calibration offsets
            yaw += calib_yaw
            pitch += calib_pitch

            # Map angles to screen coordinates
            sx = int(((yaw - (180.0 - yaw_span)) / (2.0 * yaw_span)) * screen_w)
            sy = int(((180.0 + pitch_span - pitch) / (2.0 * pitch_span)) * screen_h)

            sx = max(minx, min(minx + screen_w - 1, minx + sx))
            sy = max(miny, min(miny + screen_h - 1, miny + sy))

            # Set position directly for responsiveness
            cur.set_pos(sx, sy)

            # Minimal preview window with guidance
            cv2.putText(
                frame,
                "Press 'c' to calibrate center, 'q' to quit",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Head Cursor (Linux)", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):
            break
        if key == ord('c'):
            # Set calibration so current yaw/pitch map to screen center
            cx = 180.0
            cy = 180.0
            calib_yaw = cx - yaw
            calib_pitch = cy - pitch

    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
