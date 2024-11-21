import face_recognition
import os
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

known_faces_dir = 'known_faces'  # Directory where known faces images are stored
encodings_file = 'face_encodings.pkl'  # File to save the encodings

known_face_encodings = []
known_face_names = []

def process_image(filename):
    image_path = os.path.join(known_faces_dir, filename)
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

filenames = [filename for filename in os.listdir(known_faces_dir) if filename.endswith(('.jpg', '.png', '.jpeg'))]

for filename in filenames:
    result = process_image(filename)
    if result:
        encoding, name = result
        known_face_encodings.append(encoding)
        known_face_names.append(name)

try:
    with open(encodings_file, 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)
    logging.info(f'Encodings successfully saved to {encodings_file}')
except Exception as e:
    logging.error(f'Error saving encodings to {encodings_file}: {e}')