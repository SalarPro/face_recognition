import cv2

# Test camera 0
cap0 = cv2.VideoCapture(0)
if not cap0.isOpened():
    print("Camera 0 not accessible")
else:
    print("Camera 0 accessible")
cap0.release()

# Test camera 1
cap1 = cv2.VideoCapture(1)
cv2.waitKey(2000)

if not cap1.isOpened():
    print("Camera 1 not accessible")
else:
    print("Camera 1 accessible")
cap1.release()