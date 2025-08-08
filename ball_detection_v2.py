import cv2
import socket
import json
import numpy as np
from picamera2 import Picamera2
import time

# ==============================
# Network setup
# ==============================
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ==============================
# Camera setup
# ==============================
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start()

time.sleep(0.2)  # Warm-up

# ==============================
# Create Trackbars for HSV tuning
# ==============================
cv2.namedWindow("Trackbars")

def nothing(x):
    pass

# Initial guess for light green
cv2.createTrackbar("H Lower", "Trackbars", 35, 179, nothing)
cv2.createTrackbar("S Lower", "Trackbars", 80, 255, nothing)
cv2.createTrackbar("V Lower", "Trackbars", 120, 255, nothing)
cv2.createTrackbar("H Upper", "Trackbars", 85, 179, nothing)
cv2.createTrackbar("S Upper", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("V Upper", "Trackbars", 255, 255, nothing)

# ==============================
# Main loop
# ==============================
while True:
    # Read current HSV values from trackbars
    hL = cv2.getTrackbarPos("H Lower", "Trackbars")
    sL = cv2.getTrackbarPos("S Lower", "Trackbars")
    vL = cv2.getTrackbarPos("V Lower", "Trackbars")
    hU = cv2.getTrackbarPos("H Upper", "Trackbars")
    sU = cv2.getTrackbarPos("S Upper", "Trackbars")
    vU = cv2.getTrackbarPos("V Upper", "Trackbars")

    green_lower = np.array([hL, sL, vL], np.uint8)
    green_upper = np.array([hU, sU, vU], np.uint8)

    # Capture frame
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    h, w = frame.shape[:2]

    # Blur & convert to HSV
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Mask creation
    mask = cv2.inRange(hsv, green_lower, green_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    mask = cv2.medianBlur(mask, 5)

    # Contour detection
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ball_data = {"x": None, "y": None, "radius": None}
    info_text = "No ball detected"

    if contours:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        new_x = int(x - w/2)
        new_y = int(h/2 - y)

        if radius > 10:
            ball_data = {"x": new_x, "y": new_y, "radius": int(radius)}
            info_text = f"Ball: ({new_x}, {new_y}), r={int(radius)}"
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)

    # Send data
    sock.sendto(json.dumps(ball_data).encode(), (UDP_IP, UDP_PORT))

    # Crosshair & info
    cv2.line(frame, (w//2, 0), (w//2, h), (0, 255, 0), 1)
    cv2.line(frame, (0, h//2), (w, h//2), (0, 255, 0), 1)
    cv2.putText(frame, info_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show output
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    combined = np.hstack((frame, mask_bgr))
    cv2.imshow("Ball Detection (Left) | Mask (Right)", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()

