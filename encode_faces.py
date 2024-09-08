import face_recognition
import os
import pickle

known_faces_dir = 'known_faces'  # Directory where known faces images are stored
encodings_file = 'face_encodings.pkl'  # File to save the encodings


known_face_encodings = []
known_face_names = []

for filename in os.listdir(known_faces_dir):
    if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
        print(f'Encoding {filename}')
        image_path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if face_encodings:
            known_face_encodings.append(face_encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

with open(encodings_file, 'wb') as f:
    pickle.dump((known_face_encodings, known_face_names), f)