import os
import cv2
import face_recognition
import json
import time
import pickle

class ImageAnalyzer:
    
    setting_path = 'settings.json'
    employee_data_path = 'attendee/employee_data.json'
    face_encodings_path = 'face_data/face_encodings.pkl'
    user_images_queue_path = './user_images_queue'
    face_cascade_path = 'face_data/haarcascade_frontalface_default.xml'

    def __init__(self):
        print("ImageAnalyzer created")
        self.known_face_encodings, self.known_face_names = self.load_known_faces()
        self.accepted_percentage = self.load_settings()

    def load_known_faces(self):
        with open(self.face_encodings_path, 'rb') as f:
            known_face_encodings, known_face_names = pickle.load(f)
        return known_face_encodings, known_face_names

    def load_settings(self):
        try:
            with open(self.setting_path, 'r') as f:
                settings = json.load(f)
                return settings.get('accepted_percentage', 80)
        except Exception as e:
            print(f"Error: {e}")
            return 80

    def compare_faces(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image {image_path}")
            return "Unknown", 0

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = None
            best_match_score = float('inf')

            for index, (match, distance) in enumerate(zip(matches, face_distances)):
                if match and distance < best_match_score:
                    best_match_score = distance
                    best_match_index = index

            if best_match_index is not None and (1 - best_match_score) * 100 >= self.accepted_percentage:
                name = self.known_face_names[best_match_index]
                return name, (1 - best_match_score) * 100

        return "Unknown", 0

    def record_attendee(self, name, percentage, image_path):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        date = time.strftime("%Y-%m-%d", time.localtime())
        data = {
            "name": name,
            "timestamp": timestamp,
            "percentage": percentage,
            "image": image_path,
            "sent_to_server": False,
            "server_response": None,
        }

        if not os.path.exists(self.employee_data_path):
            employee_data = {}
        else:
            with open(self.employee_data_path, 'r') as f:
                employee_data = json.load(f)

        if date not in employee_data:
            employee_data[date] = []

        employee_data[date].append(data)

        with open(self.employee_data_path, 'w') as f:
            json.dump(employee_data, f, indent=4)

        print(f"Recorded {name} with {percentage:.2f}% similarity at {timestamp}")
        # delete the image file
        os.remove(image_path)

    def start(self):
        print("ImageAnalyzer started")
            
        if not os.path.exists(self.user_images_queue_path):
            print(f"Error: The directory {self.user_images_queue_path} does not exist.")
            return
    
        for image_file in os.listdir(self.user_images_queue_path):
            image_path = os.path.join(self.user_images_queue_path, image_file)
            if os.path.isfile(image_path) and image_file.endswith('.jpg'):
                name, percentage = self.compare_faces(image_path)
                if name != "Unknown":
                    self.record_attendee(name, percentage, image_path)
                else:
                    os.remove(image_path)

# if __name__ == "__main__":
#     analyzer = ImageAnalyzer('face_data/face_encodings.pkl', 'settings.json', 'user_images_queue')
#     analyzer.start()
