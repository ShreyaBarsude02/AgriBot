import cv2

cap = cv2.VideoCapture(0)  # Use 0 for the default camera

if not cap.isOpened():
    print("Error: Could not open camera.")
else:
    ret, frame = cap.read()
    if ret:
        height, width, _ = frame.shape
        print(f"Frame Width: {width}, Frame Height: {height}")
    else:
        print("Error: Could not read frame.")

cap.release()
