#write the ball detection logic here using opencv
#get the coordinates of the ball and convert them to direction and speed accordingly
import cv2
import socket
import json
import numpy as np
from picamera2 import Picamera2
import time

#network setup
UDP_IP = "127.0.0.1" #localhost
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 1. Initialize Picamera2
picam2 = Picamera2()
# Create a configuration for preview
camera_config = picam2.create_preview_configuration()
# Apply the configuration
picam2.configure(camera_config)
# Start the camera
picam2.start()

# Allow the camera a moment to warm up
time.sleep(0.1)

# Define the lower and upper bounds for the ball's color in HSV
# --- IMPORTANT ---
# You will likely need to TUNE these values for your specific ball and lighting!
green_lower = np.array([35, 100, 60], np.uint8)
green_upper = np.array([55, 255, 255], np.uint8)

# 2. Capture frames in a continuous loop
while True:
    # 3. Capture a frame as a NumPy array
    # This is much simpler than the old library!
    frame = picam2.capture_array()

    # --- CRITICAL STEP ---
    # Picamera2 captures in RGB format, but OpenCV uses BGR. We must convert it.
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # The rest of the detection logic is the SAME as before
    # ----------------------------------------------------

    # Blur the frame slightly
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)

    # Convert the BGR frame to the HSV color space
    hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the specified color range
    mask = cv2.inRange(hsv_frame, green_lower, green_upper)
    

    # Refine the mask using morphological operations
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # ADD THIS LINE to see the mask
    #cv2.imshow("Mask", mask)
    (h,w) = frame.shape[:2]
    # Find contours in the mask
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    center = None
    radius = 0
    info_text = ""
    #put data into the dictionary to send via UDP
    ball_data = {"x":None,"y":None, "radius":None}
    # Only proceed if at least one contour was found
    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        new_x = int(x-(w/2))
        new_y = int((h/2)-y)
        # Only draw if the radius is a reasonable size
        if radius > 10:
            ball_data = {"x":new_x,"y":new_y, "radius":int(radius)}
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 1)
            cv2.circle(frame, (int(x), int(y)), 2,(0, 0, 255), -1)
           # print(f"Ball detected: ({int(new_x)}, {int(new_y)}), radius: {int(radius)}")

    #encode data and send
    sock.sendto(json.dumps(ball_data).encode(),(UDP_IP, UDP_PORT))
    # --- Visualization ---
    # Draw a crosshair in the center of the screen to show the new origin
    cv2.line(frame, (int(w/2), 0), (int(w/2), h), (0, 255, 0), 1) # Vertical line
    cv2.line(frame, (0, int(h/2)), (w, int(h/2)), (0, 255, 0), 1) # Horizontal line

    # Put the coordinate text on the top-left of the screen
    cv2.putText(frame, info_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # Display the resulting frame
    cv2.imshow("Picamera2 Ball Detection", frame)

    # Break the loop if the 'q' key is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
# Stop the camera
picam2.stop()
