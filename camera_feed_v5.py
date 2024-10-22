import tkinter as tk
from tkinter import ttk
import cv2
import face_recognition
import pickle
import threading
import queue
import json
import time
import asyncio

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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
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
            
            if best_match_index is not None:
                name = self.known_face_names[best_match_index]
                similarity_percentage = (1 - best_match_score) * 100
                cv2.putText(frame, f"{name} ({similarity_percentage:.2f}%)", (left, top - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                current_time = time.time()
                if current_time - self.last_recorded_time > self.delay:
                    self.register_user_func(name,similarity_percentage, self.camera_index)
                    self.last_recorded_time = current_time
            else:
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        
        return frame

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")
        self.root.attributes("-topmost", True)  # Make the window always on top
        
        self.camera_threads = {}
        self.frame_queues = {}
        
        # Load known face encodings and names
        with open('face_encodings.pkl', 'rb') as f:
            self.known_face_encodings, self.known_face_names = pickle.load(f)
        
        # Load the Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        # Create GUI elements
        self.create_widgets()
        
        # Start the main loop for updating frames
        self.update_frames()
    
    def create_widgets(self):
        # Start button for exit camera
        self.start_exit_button = ttk.Button(self.root, text="Start Exit Camera", command=lambda: self.start_recognition(0))
        self.start_exit_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Start button for enter camera
        self.start_enter_button = ttk.Button(self.root, text="Start Enter Camera", command=lambda: self.start_recognition(1))
        self.start_enter_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Stop button for exit camera
        self.stop_exit_button = ttk.Button(self.root, text="Stop Exit Camera", command=lambda: self.stop_recognition(0))
        self.stop_exit_button.grid(row=1, column=0, padx=10, pady=10)
        
        # Stop button for enter camera
        self.stop_enter_button = ttk.Button(self.root, text="Stop Enter Camera", command=lambda: self.stop_recognition(1))
        self.stop_enter_button.grid(row=1, column=1, padx=10, pady=10)
    
    def start_recognition(self, camera_index):
        if camera_index not in self.camera_threads or not self.camera_threads[camera_index].running:
            frame_queue = queue.Queue()
            delay = 5  # Delay in seconds
            camera_thread = CameraThread(camera_index, self.face_cascade, self.known_face_encodings, self.known_face_names, frame_queue, self.register_user, delay)
            self.camera_threads[camera_index] = camera_thread
            self.frame_queues[camera_index] = frame_queue
            camera_thread.start()
    
    def stop_recognition(self, camera_index):
        if camera_index in self.camera_threads and self.camera_threads[camera_index].running:
            self.camera_threads[camera_index].stop()
            self.camera_threads[camera_index].join()
            del self.camera_threads[camera_index]
            del self.frame_queues[camera_index]
            # cv2.destroyAllWindows()  # Close the camera feed window if it's open
            # close the widow by title
            widowsTitle = "Enter Door" if camera_index == 1 else "Exit Door"
            cv2.destroyWindow(widowsTitle)
    
    def update_frames(self):
        for camera_index, frame_queue in self.frame_queues.items():
            if not frame_queue.empty():
                frame = frame_queue.get()
                widowsTitle = "Enter Door" if camera_index == 1 else "Exit Door"
                cv2.imshow(widowsTitle, frame)
        self.root.after(10, self.update_frames)
    
    def register_user(self, name, percentage, camera_index):
        entry_type = "exit" if camera_index == 0 else "enter"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        date = time.strftime("%Y-%m-%d", time.localtime())
        data = {
            "name": name,
            "type": entry_type,
            "timestamp": timestamp,
            "percentage": percentage,
            "sent_to_server": False,
            "server_response": None,
        }

        try:
            with open('employee_data.json', 'r') as f:
                employee_data = json.load(f)
        except FileNotFoundError:
            employee_data = {}

        if date not in employee_data:
            employee_data[date] = []

        # Check if the person is already registered for the same type on the same day
        for entry in employee_data[date]:
            if entry['name'] == name and entry['type'] == entry_type:
                print(f"{name} has already registered for {entry_type} at {entry['timestamp']}")
                return

        employee_data[date].append(data)

        with open('employee_data.json', 'w') as f:
            json.dump(employee_data, f, indent=4)

        print(f"Registered {name} for {entry_type} at {timestamp}")

class SyncDataToServer:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def sync(self):
        while True:
            if time.localtime().tm_sec == 0:
                self.calculate_data()
            
    def run(self):
        self.loop.run_until_complete(self.sync())
    
    def calculate_data(self):
        with open('employee_data.json', 'r') as f:
            employee_data = json.load(f)
        
        for date, entries in employee_data.items():
            for entry in entries:
                if not entry['sent_to_server']:
                    # Send the data to the server
                    response = self.send_data_to_server(entry)
                    entry['sent_to_server'] = True
                    entry['server_response'] = response
                    entry['sent_to_server_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        with open('employee_data.json', 'w') as f:
            json.dump(employee_data, f, indent=4)
            
    def send_data_to_server(self, data):
        # Simulate sending data to server
        print(f"Sending data to server: {data}")
        time.sleep(1)
        return "Success"

def sync_data_to_server():
    syncer = SyncDataToServer()
    syncer.run()


if __name__ == "__main__":
    thread = threading.Thread(target=sync_data_to_server)
    thread.start()
    
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()