import face_recognition
import os
import pickle
import logging

    
class EncodeFaces:
    def __init__(self):
        self.known_faces_dir = 'known_faces2'  # Directory where known faces images are stored
        self.encodings_file = 'face_data/face_encodings.pkl'  # File to save the encodings

        self.known_face_encodings = []
        self.known_face_names = []

    def process_image(self, filename):
        image_path = os.path.join(self.known_faces_dir, filename)
        try:
            logging.info(f'Processing {filename}')
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                return face_encodings[0], os.path.splitext(filename)[0]
            else:
                logging.warning(f'No faces found in {filename}')
                return None
        except Exception as e:
            logging.error(f'Error processing {filename}: {e}')
            return None

    def encode_faces(self):
        filenames = [filename for filename in os.listdir(self.known_faces_dir) if filename.endswith(('.jpg', '.png', '.jpeg'))]

        for filename in filenames:
            print(filename)
            result = self.process_image(filename)
            if result:
                encoding, name = result
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)

        try:
            with open(self.encodings_file, 'wb') as f:
                pickle.dump((self.known_face_encodings, self.known_face_names), f)
            logging.info(f'Encodings successfully saved to {self.encodings_file}')
        except Exception as e:
            logging.error(f'Error saving encodings to {self.encodings_file}: {e}')
        
        print("Done encoding faces")
