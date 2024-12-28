import os
import cv2
import face_recognition
import json
import time

def load_known_faces(known_faces_dir):
    known_face_encodings = []
    known_face_names = []
    for filename in os.listdir(known_faces_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(known_faces_dir, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(os.path.splitext(filename)[0])
    return known_face_encodings, known_face_names

def compare_faces(known_face_encodings, known_face_names, unknown_image):
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
    results = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
    face_distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)
    best_match_index = None
    best_match_score = float('inf')
    for index, (match, distance) in enumerate(zip(results, face_distances)):
        if match and distance < best_match_score:
            best_match_score = distance
            best_match_index = index
    if best_match_index is not None:
        return known_face_names[best_match_index], (1 - best_match_score) * 100
    return "Unknown", 0

def record_attendee(name, similarity_percentage):
    with open('attendees.json', 'a') as f:
        attendee_record = {
            "name": name,
            "similarity_percentage": similarity_percentage,
            "timestamp": time.time()
        }
        json.dump(attendee_record, f)
        f.write('\n')

def main():
    user_images_queue_dir = os.path.join(os.path.dirname(__file__), 'user_images_queue')
    known_faces_dir = os.path.join(os.path.dirname(__file__), 'known_faces')

    known_face_encodings, known_face_names = load_known_faces(known_faces_dir)

    for filename in os.listdir(user_images_queue_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(user_images_queue_dir, filename)
            unknown_image = face_recognition.load_image_file(image_path)
            name, similarity_percentage = compare_faces(known_face_encodings, known_face_names, unknown_image)
            record_attendee(name, similarity_percentage)
            print(f"Recorded {name} with {similarity_percentage:.2f}% similarity")

if __name__ == "__main__":
    main()