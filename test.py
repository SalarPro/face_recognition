import cv2
import os

def save_frame(frame):
    # cv2.imwrite('tmp/frame.jpg', frame)
    # get the full path of the file
    # full_path = os.path.join(os.getcwd(), 'tmp', 'frame.jpg')
    my_absolute_dirpath = os.path.abspath(os.path.dirname(__file__))

    tmp_dir = os.path.join(my_absolute_dirpath, 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    full_path = os.path.join(tmp_dir, 'frame.jpg')

    print(full_path)
    if cv2.imwrite(full_path, frame) == True:
        print(f"Image saved as {full_path}")
    else:
        print("Error: Could not save image.")

    
    
    
# Open a connection to the camera
print("It' started")
startTime = cv2.getTickCount()
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
endTime = cv2.getTickCount()
print("Elapsed time: %.2f ms" % ((endTime - startTime) / cv2.getTickFrequency() * 1000))

print("It' started")

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

ret, frame = cap.read()
if ret:
    cv2.imshow('Camera Test', frame)
    # SAVE THE FRAME AS IMAGE TO /tmp IF THE tmp DIRECTORY EXISTS else current directory
    save_frame(frame)

    cv2.waitKey(0)
else:
    print("Error: Could not read frame.")

cap.release()
cv2.destroyAllWindows()


