import cv2 

import numpy as np 

import RPi.GPIO as GPIO 

from collections import deque 

  

# Define HSV range for detecting blue objects 

blueLower = (100, 150, 0) 

blueUpper = (140, 255, 255) 

  

# Initialize deque for storing tracked points 

pts = deque(maxlen=64) 

  

# Define servo pins (change according to your setup) 

PAN_PIN = 17  # GPIO pin for pan servo 

TILT_PIN = 18  # GPIO pin for tilt servo 

  

# Initialize GPIO 

GPIO.setmode(GPIO.BCM) 

GPIO.setup(PAN_PIN, GPIO.OUT) 

GPIO.setup(TILT_PIN, GPIO.OUT) 

  

# Initialize PWM for pan and tilt (adjust frequency if needed) 

pan_servo = GPIO.PWM(PAN_PIN, 50)  # 50 Hz PWM frequency 

tilt_servo = GPIO.PWM(TILT_PIN, 50)  # 50 Hz PWM frequency 

pan_servo.start(7.5)  # Start with middle position (0°) 

tilt_servo.start(7.5)  # Start with middle position (0°) 

  

# Open the camera stream using GStreamer 

cap = cv2.VideoCapture("libcamerasrc ! video/x-raw, format=NV12 ! videoconvert ! appsink", cv2.CAP_GSTREAMER) 

  

if not cap.isOpened(): 

    print("Failed to open camera") 

    exit() 

  

# Camera frame dimensions (adjust based on your camera's resolution) 

frame_width = 600 

frame_height = 480 

  

while True: 

    # Capture frame-by-frame 

    ret, frame = cap.read() 

    if not ret: 

        print("Failed to grab frame. Exiting...") 

        break 

  

    # Resize the frame 

    frame = cv2.resize(frame, (frame_width, frame_height)) 

  

    # Apply Gaussian blur and convert to HSV 

    blurred = cv2.GaussianBlur(frame, (11, 11), 0) 

    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) 

  

    # Create a mask for blue color 

    mask = cv2.inRange(hsv, blueLower, blueUpper) 

    mask = cv2.erode(mask, None, iterations=2) 

    mask = cv2.dilate(mask, None, iterations=2) 

  

    # Find contours 

    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    center = None 

  

    # Process contours if any are found 

    if len(cnts) > 0: 

        # Find the largest contour 

        c = max(cnts, key=cv2.contourArea) 

        ((x, y), radius) = cv2.minEnclosingCircle(c) 

        M = cv2.moments(c) 

  

        # Calculate center only if moments are valid 

        if M["m00"] != 0: 

            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) 

  

        # Draw the circle and centroid if radius is sufficient 

        if radius > 10: 

            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2) 

            cv2.circle(frame, center, 5, (0, 0, 255), -1) 

  

        # Calculate pan and tilt angles 

        pan_angle = np.interp(center[0], [0, frame_width], [0, 180])  # Map X position to pan 

        tilt_angle = np.interp(center[1], [0, frame_height], [0, 180])  # Map Y position to tilt 

  

        # Set the servo positions based on the mapped angles 

        pan_servo.ChangeDutyCycle(pan_angle / 18 + 2.5)  # Adjust duty cycle for servo (0-180 degrees) 

        tilt_servo.ChangeDutyCycle(tilt_angle / 18 + 2.5)  # Adjust duty cycle for servo (0-180 degrees) 

  

    # Append center to the deque 

    pts.appendleft(center) 

  

    # Draw the tracking lines 

    for i in range(1, len(pts)): 

        if pts[i - 1] is None or pts[i] is None: 

            continue 

        thickness = int(np.sqrt(64 / float(i + 1)) * 2.5) 

        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness) 

  

    # Display the frame and mask 

    cv2.imshow("Frame", frame) 

    cv2.imshow("Mask", mask) 

  

    # Break the loop if 'q' is pressed 

    key = cv2.waitKey(1) & 0xFF 

    if key == ord("q"): 

        break 

  

# Release the video capture, stop PWM, and clean up GPIO 

cap.release() 

pan_servo.stop() 

tilt_servo.stop() 

GPIO.cleanup() 

cv2.destroyAllWindows() 
