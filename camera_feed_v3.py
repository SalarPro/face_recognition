import cv2
import face_recognition
import pickle

# Load known face encodings and names
with open('face_encodings.pkl', 'rb') as f:
    known_face_encodings, known_face_names = pickle.load(f)

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Open two cameras (0 for entrance, 1 for exit)
cap_entrance = cv2.VideoCapture(0)
cap_exit = cv2.VideoCapture(1)

# sleep for 5 seconds
cv2.waitKey(1000)

if not cap_entrance.isOpened() or not cap_exit.isOpened():
    print("Error: Could not open one or both cameras.")
    exit()

# Resize factors for the camera windows
resize_factor = 0.5  # Change this value as needed

while True:
    ret_entrance, frame_entrance = cap_entrance.read()
    ret_exit, frame_exit = cap_exit.read()

    if ret_entrance and ret_exit:
        # Process entrance camera frame
        gray_entrance = cv2.cvtColor(frame_entrance, cv2.COLOR_BGR2GRAY)
        faces_entrance = face_cascade.detectMultiScale(gray_entrance, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        face_locations_entrance = []
        for (x, y, w, h) in faces_entrance:
            face_locations_entrance.append((y, x + w, y + h, x))

        face_encodings_entrance = face_recognition.face_encodings(frame_entrance, face_locations_entrance)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations_entrance, face_encodings_entrance):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            best_match_index = None
            best_match_score = float('inf')

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            for index, (match, distance) in enumerate(zip(matches, face_distances)):
                if match and distance < best_match_score:
                    best_match_score = distance
                    best_match_index = index

            if best_match_index is not None:
                name = known_face_names[best_match_index]
                similarity_percentage = (1 - best_match_score) * 100
                cv2.putText(frame_entrance, f"{name} ({similarity_percentage:.2f}%)", (left, top - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
            else:
                cv2.putText(frame_entrance, name, (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)

            cv2.rectangle(frame_entrance, (left, top), (right, bottom), (255, 0, 0), 2)

        # Resize the entrance camera frame
        frame_entrance_resized = cv2.resize(frame_entrance, (int(frame_entrance.shape[1] * resize_factor), int(frame_entrance.shape[0] * resize_factor)))

        # Process exit camera frame
        gray_exit = cv2.cvtColor(frame_exit, cv2.COLOR_BGR2GRAY)
        faces_exit = face_cascade.detectMultiScale(gray_exit, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        face_locations_exit = []
        for (x, y, w, h) in faces_exit:
            face_locations_exit.append((y, x + w, y + h, x))

        face_encodings_exit = face_recognition.face_encodings(frame_exit, face_locations_exit)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations_exit, face_encodings_exit):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            best_match_index = None
            best_match_score = float('inf')

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            for index, (match, distance) in enumerate(zip(matches, face_distances)):
                if match and distance < best_match_score:
                    best_match_score = distance
                    best_match_index = index

            if best_match_index is not None:
                name = known_face_names[best_match_index]
                similarity_percentage = (1 - best_match_score) * 100
                cv2.putText(frame_exit, f"{name} ({similarity_percentage:.2f}%)", (left, top - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1)
            else:
                cv2.putText(frame_exit, name, (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1)

            cv2.rectangle(frame_exit, (left, top), (right, bottom), (255, 0, 0), 2)

        # Resize the exit camera frame
        frame_exit_resized = cv2.resize(frame_exit, (int(frame_exit.shape[1] * resize_factor), int(frame_exit.shape[0] * resize_factor)))

        # Display the results
        cv2.imshow('Entrance Camera Feed - Face Recognition', frame_entrance_resized)
        cv2.imshow('Exit Camera Feed - Face Recognition', frame_exit_resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("Error: Could not read frames from one or both cameras.")
        break

cap_entrance.release()
cap_exit.release()
cv2.destroyAllWindows()
