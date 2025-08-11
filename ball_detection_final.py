import cv2
import socket
import json
import numpy as np
from picamera2 import Picamera2
import time

# ==============================
# Network setup
# ==============================
UDP_IP = "127.0.0.1"  # localhost
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ==============================
# Camera setup
# ==============================
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start()

# Allow camera to warm up
time.sleep(0.1)

# ==============================
# HSV Range for LIGHT GREEN ball
# (Tune these if needed)
# ==============================
# Light green tends to be around H: 35-85, S: medium-high, V: high
green_lower = np.array([35, 100, 60], np.uint8)
green_upper = np.array([55, 255, 255], np.uint8)

# ==============================
# Main loop
# ==============================
while True:
    # Capture frame as NumPy array (RGB from PiCamera2)
    frame = picam2.capture_array()

    # Convert RGB -> BGR for OpenCV
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    h, w = frame.shape[:2]

    # Blur to reduce noise
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)

    # Convert to HSV
    hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    # Mask for green
    mask = cv2.inRange(hsv_frame, green_lower, green_upper)

    # Noise reduction: erode → dilate (open), then median blur
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    mask = cv2.medianBlur(mask, 5)

    # Find contours
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Data to send
    ball_data = {"x": None, "y": None, "radius": None}
    info_text = "No ball detected"

    if contours:
        # Largest contour
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        new_x = int(x - (w / 2))      # X relative to center
        new_y = int((h / 2) - y)      # Y relative to center (inverted)

        if radius > 10:  # Ignore very small blobs
            ball_data = {"x": new_x, "y": new_y, "radius": int(radius)}
            info_text = f"Ball: ({new_x}, {new_y}), r={int(radius)}"

            # Draw ball and center
            #cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 1)
            #cv2.circle(frame, (int(x), int(y)), 2, (0, 0, 255), -1)

    # Send via UDP
    sock.sendto(json.dumps(ball_data).encode(), (UDP_IP, UDP_PORT))

    # Draw crosshair
    #cv2.line(frame, (w // 2, 0), (w // 2, h), (0, 255, 0), 1)
    #cv2.line(frame, (0, h // 2), (w, h // 2), (0, 255, 0), 1)

    # Show info text
    #cv2.putText(frame, info_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show camera feed and mask side-by-side
    #mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    #cv2.imshow("Ball Detection", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
picam2.stop()

