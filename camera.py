import numpy as np
import cv2
import RPi.GPIO as GPIO
import time
from datetime import datetime

BUTTON_PIN = 16  # GPIO pin for button
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4656)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3496)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

def take_snapshot(frame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = f"snapshot_{timestamp}.png"
    frame_resized = cv2.resize(frame, (640, 480))
    cv2.imwrite(img_name, frame)
    cv2.imshow("Snapshot", frame_resized)
    print(f"{img_name} written!")
    cv2.waitKey(2000)
    cv2.destroyWindow("Snapshot")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame_resized = cv2.resize(frame, (640, 480))
        cv2.imshow('Live Stream', frame_resized)

        # Button press takes a snapshot
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            take_snapshot(frame)
            time.sleep(0.5)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
