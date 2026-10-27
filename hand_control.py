import math
import time
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker:
    def __init__(self, camera_index=0, model_path=None):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(
                "Could not open a webcam. Check camera permissions or pass a different camera_index."
            )

        self.model_path = Path(model_path) if model_path else Path(__file__).resolve().parent / "hand_landmarker.task"
        if not self.model_path.is_file():
            self.cap.release()
            raise FileNotFoundError(f"Hand-landmarker model not found: {self.model_path}")

        try:
            base_options = python.BaseOptions(model_asset_path=str(self.model_path))
            options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
            self.detector = vision.HandLandmarker.create_from_options(options)
        except Exception:
            self.cap.release()
            raise

        self.prev_x = None
        self.smooth_factor = 0.7
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.3
        self.combo_sequence = []
        self.combo_time_limit = 1.5
        self.last_combo_time = time.time()
        self.frame = None
        self.current_color = (255, 255, 255)

    def detect_gesture(self, landmarks):
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]

        pinch_dist = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)
        fist_dist = math.hypot(wrist.x - middle_tip.x, wrist.y - middle_tip.y)
        fingers_open = (
            index_tip.y < landmarks[6].y
            and middle_tip.y < landmarks[10].y
            and ring_tip.y < landmarks[14].y
            and pinky_tip.y < landmarks[18].y
        )
        index_up = index_tip.y < landmarks[6].y and middle_tip.y > landmarks[10].y

        current_time = time.time()
        gesture = None
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None

        if pinch_dist < 0.04:
            gesture = "pinch"
            self.current_color = (255, 0, 0)
        elif fist_dist < 0.12:
            gesture = "fist"
            self.current_color = (255, 0, 255)
        elif fingers_open:
            gesture = "open"
            self.current_color = (255, 255, 255)
        elif index_up:
            gesture = "laser"
            self.current_color = (0, 255, 255)

        if gesture:
            self.last_gesture_time = current_time
            self.combo_sequence.append(gesture)
        return gesture

    def check_combo(self):
        current_time = time.time()
        if current_time - self.last_combo_time > self.combo_time_limit:
            self.combo_sequence = []

        if self.combo_sequence[-3:] == ["pinch", "open", "fist"]:
            self.combo_sequence = []
            self.last_combo_time = current_time
            return "SPECIAL"
        return None

    def draw_hand_effects(self, frame, landmarks, gesture):
        h, w, _ = frame.shape
        for landmark in landmarks:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, self.current_color, -1)

        finger_pairs = [
            (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12), (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
        ]
        for start_idx, end_idx in finger_pairs:
            start, end = landmarks[start_idx], landmarks[end_idx]
            cv2.line(
                frame,
                (int(start.x * w), int(start.y * h)),
                (int(end.x * w), int(end.y * h)),
                self.current_color,
                2,
            )

        if gesture == "laser":
            index_tip = landmarks[8]
            x, y = int(index_tip.x * w), int(index_tip.y * h)
            cv2.line(frame, (x, y), (x, 0), (0, 0, 255), 4)

    def get_hand_data(self):
        success, frame = self.cap.read()
        if not success:
            return None

        frame = cv2.flip(frame, 1)
        self.frame = frame.copy()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.detector.detect(mp_image)

        if not result.hand_landmarks:
            return None

        landmarks = result.hand_landmarks[0]
        height, width, _ = frame.shape
        raw_x = int(landmarks[8].x * width)
        smooth_x = raw_x if self.prev_x is None else int(
            self.smooth_factor * self.prev_x + (1 - self.smooth_factor) * raw_x
        )
        self.prev_x = smooth_x
        gesture = self.detect_gesture(landmarks)
        combo = self.check_combo()
        if combo:
            gesture = combo
        self.draw_hand_effects(frame, landmarks, gesture)
        self.frame = frame

        return {"x": smooth_x, "gesture": gesture, "color": self.current_color}

    def get_frame(self):
        return self.frame

    def release(self):
        if getattr(self, "cap", None) is not None:
            self.cap.release()
        if getattr(self, "detector", None) is not None:
            self.detector.close()
