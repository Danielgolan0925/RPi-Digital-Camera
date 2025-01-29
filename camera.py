import numpy as np
import cv2
import RPi.GPIO as GPIO
import time
from datetime import datetime

BUTTON_PIN = 16 # GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

def take_snapshot(frame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = f"snapshot_{timestamp}.png"
    cv2.imwrite(img_name, frame)
    print(f"{img_name} written!")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow('Live Stream', frame)

        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            take_snapshot(frame)
            time.sleep(0.5)  # Debounce delay

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()