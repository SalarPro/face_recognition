import cv2
import face_recognition
import threading
import json
import time
import os


class CameraThread(threading.Thread):

    accepted_percentage = 80
    
    last_recorded_time2 = 0
    each_frame_latency = 1 #ms
    
    remove_user_registered = 0
    user_image_path = ""
    
    setting_path = 'settings.json'
    employee_data_path = 'attendee/employee_data.json'
    face_encodings_path = 'face_data/face_encodings.pkl'
    user_images_queue_path = '../user_images_queue'
    face_cascade_path = 'face_data/haarcascade_frontalface_default.xml'
    
    
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
        try:
            with open(self.setting_path, 'r') as f:
                settings = json.load(f)
                accepted_percentage = settings['accepted_percentage']
                # check if is number else between 0 and 100 else 80
                self.accepted_percentage = accepted_percentage if accepted_percentage and 0 <= accepted_percentage <= 100 else 80
        except Exception as e:
            print(f"Error123: {e}")
            
        self.last_recorded_time2 = time.time()
        self.remove_user_registered = time.time()

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        
        # Check if the camera is opened successfully
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}.")
            return
        
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # frame = self.process_frame(frame)
                frame = self.process_frame_without_comparing(frame)
                self.frame_queue.put(frame)
            else:
                print(f"Error: Could not read frame from camera {self.camera_index}.")
                self.stop()
        
        self.cap.release()

    def stop(self):
        self.running = False
    
    

    def process_frame(self, frame):
        
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
            
            if best_match_index is not None and (1 - best_match_score) * 100 < self.accepted_percentage:
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


    def process_frame_without_comparing(self, frame):
        # only show rectangles around faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=6, minSize=(150, 150), flags=cv2.CASCADE_SCALE_IMAGE)
        
        current_time = time.time()
        # print those values: current_time - self.last_recorded_time2 > self.each_frame_latency
        if current_time - self.last_recorded_time2 > self.delay and len(faces) > 0:#
            imgRes = self.save_frame(frame)
            self.last_recorded_time2 = current_time
            self.remove_user_registered = current_time + 1.8
            self.user_image_path = imgRes
        
        for (x, y, w, h) in faces:
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 6)
            # draw rounded rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2, cv2.FILLED, 0)
            
        #save a copy of the frame to /user_images
        # if remove_user_registered > current_time: show user image in the button corner of the screen
        if self.remove_user_registered > current_time and self.user_image_path != "":
            # print(f"User image path: {self.user_image_path}")
            user_img = cv2.imread(self.user_image_path)
            user_img = cv2.resize(user_img, (200, 150))
            # 3:4 aspect ratio
            # get screen width and height
            screen_width = frame.shape[1]
            screen_height = frame.shape[0]
            # frame[screen_height-150:screen_height, 0:200] = user_img
            # button right
            frame[0:150, screen_width-200:screen_width] = user_img
            # add text saying "Welcome" to the user
            # cv2.putText(frame, "Welcome", (screen_width-200, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            

        
        return frame

    def save_frame(self, frame):
        # cv2.imwrite('tmp/frame.jpg', frame)
        # get the full path of the file
        # full_path = os.path.join(os.getcwd(), 'tmp', 'frame.jpg')
        my_absolute_dirpath = os.path.abspath(os.path.dirname(__file__))

        tmp_dir = os.path.join(my_absolute_dirpath, self.user_images_queue_path)
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        cTime = time.time()
        full_path = os.path.join(tmp_dir, f'f_{cTime}.jpg')

        if cv2.imwrite(full_path, frame) == True:
            print(f"Image saved as {full_path}")
        else:
            print("Error: Could not save image.")
        return full_path