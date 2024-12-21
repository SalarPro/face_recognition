import cv2

# Open a connection to the camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

ret, frame = cap.read()
if ret:
    cv2.imshow('Camera Test', frame)
    cv2.waitKey(0)
else:
    print("Error: Could not read frame.")

cap.release()
cv2.destroyAllWindows()