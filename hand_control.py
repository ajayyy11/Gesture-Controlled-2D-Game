import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import time

class HandTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        base_options = python.BaseOptions(
            model_asset_path="hand_landmarker.task"
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

        self.prev_x = None
        self.smooth_factor = 0.7

        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5  # seconds

    def detect_gesture(self, landmarks):

        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]

        pinch_dist = math.hypot(
            thumb_tip.x - index_tip.x,
            thumb_tip.y - index_tip.y
        )

        fingers_open = (
            index_tip.y < landmarks[6].y and
            middle_tip.y < landmarks[10].y and
            ring_tip.y < landmarks[14].y and
            pinky_tip.y < landmarks[18].y
        )

        fist_dist = math.hypot(
            wrist.x - middle_tip.x,
            wrist.y - middle_tip.y
        )

        current_time = time.time()

        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None

        if pinch_dist < 0.04:
            self.last_gesture_time = current_time
            return "pinch"

        if fist_dist < 0.12:
            self.last_gesture_time = current_time
            return "fist"

        if fingers_open:
            return "open"

        return None

    def get_hand_data(self):
        success, frame = self.cap.read()
        if not success:
            return None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = self.detector.detect(mp_image)

        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            h, w, _ = frame.shape

            raw_x = int(landmarks[8].x * w)

            # Smoothing
            if self.prev_x is None:
                smooth_x = raw_x
            else:
                smooth_x = int(
                    self.smooth_factor * self.prev_x +
                    (1 - self.smooth_factor) * raw_x
                )

            self.prev_x = smooth_x

            gesture = self.detect_gesture(landmarks)

            cv2.imshow("Camera", frame)
            cv2.waitKey(1)

            return {"x": smooth_x, "gesture": gesture}

        cv2.imshow("Camera", frame)
        cv2.waitKey(1)
        return None

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()