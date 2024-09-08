import cv2
import face_recognition
import pickle

# Load known face encodings and names
with open('face_encodings.pkl', 'rb') as f:
    known_face_encodings, known_face_names = pickle.load(f)

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Open the default camera
cap = cv2.VideoCapture(0)

# wait for 5 seconds
# cv2.waitKey(5000)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = cap.read()

    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        face_locations = []
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))

        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            best_match_index = None
            best_match_score = float('inf')

            # Calculate face distances and find the best match
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            for index, (match, distance) in enumerate(zip(matches, face_distances)):
                if match and distance < best_match_score:
                    best_match_score = distance
                    best_match_index = index

            if best_match_index is not None:
                name = known_face_names[best_match_index]
                # Convert distance to percentage
                similarity_percentage = (1 - best_match_score) * 100
                cv2.putText(frame, f"{name} ({similarity_percentage:.2f}%)", (left, top - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (00, 255, 000), 1)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            else:
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw rectangle around face

        cv2.imshow('Camera Feed - Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("Error: Could not read frame.")
        break

cap.release()
cv2.destroyAllWindows()
