import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- CONFIGURATION ---
model_path = 'efficientdet.tflite'

# 1. Initialize Object Detector
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)

# 2. Initialize Face Mesh (Eye Tracking)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Convert to RGB (MediaPipe requirement)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # --- TASK 1: Detection (Phone/Distractions) ---
    detection_result = detector.detect(mp_image)
    for detection in detection_result.detections:
        category = detection.categories[0].category_name
        if category in ['cell phone', 'book']:
            print(f"DISTRACTION DETECTED: {category}")

    # --- TASK 2: Eye Tracking ---
    face_results = face_mesh.process(rgb_frame)
    if face_results.multi_face_landmarks:
        # Index 468 is the center of the left iris
        iris_pos = face_results.multi_face_landmarks[0].landmark[468]
        # If iris_pos moves too far left/right, they aren't looking at screen
        if iris_pos.x < 0.4 or iris_pos.x > 0.6:
            print("NOT LOOKING AT SCREEN")

    cv2.imshow('Focus Monitor', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()