import numpy as np
import cv2
import RPi.GPIO as GPIO
import time
from datetime import datetime

BUTTON_PIN = 16  # GPIO pin for button (you can remove this if you're not using GPIO)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320

# Define button sizes as percentages of the screen resolution
button_w = int(400)  # 30% of screen width
button_h = int(150)  # 15% of screen height
quit_button_w = button_w  # Keeping same width for quit button
quit_button_h = button_h  # Keeping same height for quit button

# Position buttons proportionally on the screen
button_x = int(100)  # 10% from the left
button_y = int(100)  # 10% from the top
quit_button_x = int(3340)  # 10% from the left
quit_button_y = int(100)  # 30% from the top

snapshot = None
snapshot_time = 0
SNAPSHOT_DURATION = 2  # Display snapshot for 2 seconds

def take_snapshot(frame):
    global snapshot, snapshot_time

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = f"snapshot_{timestamp}.png"
    cv2.imwrite(img_name, frame)
    print(f"{img_name} written!")

    # Store the resized snapshot and timestamp it
    snapshot = cv2.resize(frame, (3840, 2160))
    snapshot_time = time.time()

def click_event(event, x, y, flags, param):
    global running

    if event == cv2.EVENT_LBUTTONDOWN:
        if button_x <= x <= button_x + button_w and button_y <= y <= button_y + button_h:
            print("Snapshot button clicked!")
            ret, frame = cap.read()
            if ret:
                take_snapshot(frame)

        elif quit_button_x <= x <= quit_button_x + quit_button_w and quit_button_y <= y <= quit_button_y + quit_button_h:
            print("Quit button clicked! Exiting...")
            running = False
            cap.release()
            cv2.destroyAllWindows()
            GPIO.cleanup()
            exit()

cv2.namedWindow("Live Stream", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Live Stream", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("Live Stream", click_event)

running = True

try:
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Draw buttons
        cv2.rectangle(frame, (button_x, button_y), (button_x + button_w, button_y + button_h), (0, 255, 0), -1)
        cv2.rectangle(frame, (quit_button_x, quit_button_y), (quit_button_x + quit_button_w, quit_button_y + quit_button_h), (0, 0, 255), -1)

        # Center text in buttons
        text_size, _ = cv2.getTextSize("Snapshot", cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_x = button_x + (button_w - text_size[0]) // 2
        text_y = button_y + (button_h + text_size[1]) // 2
        cv2.putText(frame, "Snapshot", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        text_size, _ = cv2.getTextSize("Quit", cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_x = quit_button_x + (quit_button_w - text_size[0]) // 2
        text_y = quit_button_y + (quit_button_h + text_size[1]) // 2
        cv2.putText(frame, "Quit", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Display snapshot for 2 seconds
        if snapshot is not None and (time.time() - snapshot_time) < SNAPSHOT_DURATION:
            # Get frame dimensions
            frame_h, frame_w, _ = frame.shape
            snap_h, snap_w = snapshot.shape[:2]
        
            # Calculate center position
            x1, y1 = (frame_w - snap_w) // 2, (frame_h - snap_h) // 2
            x2, y2 = x1 + snap_w, y1 + snap_h
        
            # Ensure snapshot fits within frame dimensions
            frame[y1:y2, x1:x2] = snapshot
        elif snapshot is not None:
            snapshot = None  # Remove snapshot after 2 seconds

        cv2.imshow('Live Stream', frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or not running:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()
