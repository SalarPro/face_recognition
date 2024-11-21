import face_recognition
import cv2

# Load sample images and encode known faces
known_face_encodings = []
known_face_names = []

# Encode known faces
image1 = face_recognition.load_image_file("known_faces/azad.png")
face_encoding1 = face_recognition.face_encodings(image1)[0]
known_face_encodings.append(face_encoding1)
known_face_names.append("Person 1")

image2 = face_recognition.load_image_file("known_faces/salar_v3.png")
face_encoding2 = face_recognition.face_encodings(image2)[0]
known_face_encodings.append(face_encoding2)
known_face_names.append("Person 2")

# Initialize variables
face_locations = []
face_encodings = []
face_names = []

# Open video capture
video_capture = cv2.VideoCapture(1)

# await 3 seconds for camera to start
cv2.waitKey(3000)

while True:
    # Read video frame
    print(0)
    ret, frame = video_capture.read()
    print(1)

    # Resize frame for faster processing (optional)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    print(2)

    # Convert the image from BGR color (OpenCV default) to RGB color
    rgb_small_frame = small_frame[:, :, ::-1]
    print(3)

    # Find all the faces and their encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    print(4)

    # Ensure face_locations is in the correct format
    if not all(isinstance(loc, tuple) and len(loc) == 4 for loc in face_locations):
        print("Error: face_locations is not in the correct format")
        continue

    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    print(5)

    face_names = []
    print(6)
    for face_encoding in face_encodings:
        print(7)
        # Compare face encoding with known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # If a match is found, use the known face name
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_names.append(name)

    # Display results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since we scaled them down
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()