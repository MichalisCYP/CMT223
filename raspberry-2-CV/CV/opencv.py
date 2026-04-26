import cv2
import os
import time

# 1. Load Face AND Eye cascades
face_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
eye_path = '/usr/share/opencv4/haarcascades/haarcascade_eye.xml'

face_cascade = cv2.CascadeClassifier(face_path)
eye_cascade = cv2.CascadeClassifier(eye_path)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Settings for Posture
STANDARD_Y = None  # We will calibrate this on start

while True:
    ret, img = cap.read()
    if not ret: break
    
    img = cv2.flip(img, 1) # Mirror view
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    status = "Looking Away!"
    color = (0, 0, 255) # Red

    for (x, y, w, h) in faces:
        # Draw face box
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2)
        
        # Calibrate posture on first sight
        if STANDARD_Y is None: STANDARD_Y = y
        
        # Check Posture (Slouching)
        if y > STANDARD_Y + 40:
            cv2.putText(img, "FIX POSTURE!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # Look for eyes INSIDE the face area
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        
        if len(eyes) >= 2:
            status = "Focused"
            color = (0, 255, 0) # Green
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(img, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)
        else:
            status = "Eyes Not Detected"

    # Display Status
    cv2.putText(img, f"Status: {status}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.imshow('Advanced Monitor', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()