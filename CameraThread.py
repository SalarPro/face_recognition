import cv2
import face_recognition
import threading
import json
import time


class CameraThread(threading.Thread):
    def __init__(self, camera_index, face_cascade, known_face_encodings, known_face_names, frame_queue, register_user_func, delay):
        super().__init__()
        self.camera_index = camera_index
        self.face_cascade = face_cascade
        self.known_face_encodings = known_face_encodings
        self.known_face_names = known_face_names
        self.frame_queue = frame_queue
        self.register_user_func = register_user_func
        self.delay = delay
        self.cap = None
        self.running = False
        self.last_recorded_time = 0

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        #sleep for 1 second to make sure the camera is opened
        time.sleep(1)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}.")
            return
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = self.process_frame(frame)
                self.frame_queue.put(frame)
            else:
                print(f"Error: Could not read frame from camera {self.camera_index}.")
                self.stop()
        self.cap.release()

    def stop(self):
        self.running = False
    
    

    def process_frame(self, frame):
        accepted_percentage = 80
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                accepted_percentage = settings['accepted_percentage']
                # check if is number else between 0 and 100 else 80
                accepted_percentage = accepted_percentage if accepted_percentage and 0 <= accepted_percentage <= 100 else 80
        except Exception as e:
            print(f"Error123: {e}")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=7, minSize=(250, 250))
        
        face_locations = []
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))
        
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            best_match_index = None
            best_match_score = float('inf')
            
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            for index, (match, distance) in enumerate(zip(matches, face_distances)):
                if match and distance < best_match_score:
                    best_match_score = distance
                    best_match_index = index

            
            
            if best_match_index is not None and (1 - best_match_score) * 100 < accepted_percentage:
                continue
            
            
            if best_match_index is not None:
                name = self.known_face_names[best_match_index]
                similarity_percentage = (1 - best_match_score) * 100
                cv2.putText(frame, f"{name} ({similarity_percentage:.2f}%)", (left, top - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                current_time = time.time()
                current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if current_time - self.last_recorded_time > self.delay:
                    self.register_user_func(name,similarity_percentage, self.camera_index, current_frame)
                    self.last_recorded_time = current_time
            else:
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        
        return frame
