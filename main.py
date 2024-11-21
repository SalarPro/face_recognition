import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import pickle
import threading
import queue
import json
import time
from setting_window import SettingsWindow
from tkinter import PhotoImage
from sync_data_to_server import SyncDataToServer
from CameraThread import CameraThread


camera_id_exit = 0
camera_id_enter = 1


class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kavin | face recognition attendance system")
        self.root.attributes("-topmost", True)  # Make the window always on top
        icon = PhotoImage(file="ico.png")
        self.root.iconphoto(True, icon)
        # put to the center of the screen
        self.root.geometry("800x500+{}+{}".format(int(self.root.winfo_screenwidth()/2 - 250), int(self.root.winfo_screenheight()/2 - 250)))
        # make it start in the second monitor
        
        
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
    
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        app = SettingsWindow(settings_window)
        app.run()

        
    
    def create_widgets(self):
        
        # get camera_id_exit camera_id_enter from settings.json

        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                camera_id_exit = settings['camera_id_exit']
                camera_id_enter = settings['camera_id_enter']
        except Exception as e:
            print(f"Error: {e}")
            camera_id_exit = 0
            camera_id_enter = 1
            
        
        self.lbl1 = ttk.Label(self.root, text="Developed by Z Tech .office")
        self.lbl1.grid(row=10, column=10, padx=10, pady=50)
        # Start button for exit camera
        self.start_exit_button = ttk.Button(self.root, text="Start Exit Camera", command=lambda: self.start_recognition(camera_id_exit))
        self.start_exit_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Start button for enter camera
        self.start_enter_button = ttk.Button(self.root, text="Start Enter Camera", command=lambda: self.start_recognition(camera_id_enter))
        self.start_enter_button.grid(row=0, column=1, padx=10, pady=10)
        
        # Stop button for exit camera
        self.stop_exit_button = ttk.Button(self.root, text="Stop Exit Camera", command=lambda: self.stop_recognition(camera_id_exit))
        self.stop_exit_button.grid(row=1, column=0, padx=10, pady=10)
        
        # Stop button for enter camera
        self.stop_enter_button = ttk.Button(self.root, text="Stop Enter Camera", command=lambda: self.stop_recognition(camera_id_enter))
        self.stop_enter_button.grid(row=1, column=1, padx=10, pady=10)
        
        
        # add tow frame to show the camera feed
        # frame for exit camera
        self.exit_frame = ttk.Frame(self.root, width=100, height=100)
        self.exit_frame.grid(row=2, column=0, padx=10, pady=10)
        # pring all ttk.Frame attributes
        
        # frame for enter camera
        self.enter_frame = ttk.Frame(self.root, width=100, height=100)
        self.enter_frame.grid(row=2, column=1, padx=10, pady=10)
        # make bg color white
    
        # add new button for setting and open setting_window.py
        self.setting_button = ttk.Button(self.root, text="Settings", command=lambda: self.open_settings())
        self.setting_button.grid(row=3, column=0, padx=10, pady=10)
        
        # add new button for setting and open setting_window.py
        self.callServer = ttk.Button(self.root, text="CALL Server", command=lambda: SyncDataToServer().calculate_data())
        self.callServer.grid(row=4, column=0, padx=10, pady=10)
        
    def start_recognition(self, camera_index):
        if camera_index not in self.camera_threads or not self.camera_threads[camera_index].running:
            frame_queue = queue.Queue()
            wt_for_each_frame = 1
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    wt_for_each_frame = settings['wt_for_each_frame'] # time in seconds
                    # if wt_for_each_frame is number else 0
                    wt_for_each_frame = wt_for_each_frame if wt_for_each_frame else 0
            except Exception as e:
                print(f"Error: {e}")
                
            delay = wt_for_each_frame
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
        self.root.after(5, self.update_frames)
    
    def register_user(self, name, percentage, camera_index, current_frame):
        accepted_percentage = 80
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                accepted_percentage = settings['accepted_percentage']
                # check if is number else between 0 and 100 else 80
                accepted_percentage = accepted_percentage if accepted_percentage and 0 <= accepted_percentage <= 100 else 80
        except Exception as e:
            print(f"Error: {e}")
        
        
        if percentage < accepted_percentage:
            return
        
        
        entry_type = "exit" if camera_index == camera_id_exit else "enter"
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
        
        # save frame to the user_images folder and give it current time as name
        cv2.imwrite(f"user_images/{name}_{timestamp}.jpg", cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR))
        fileName = f"user_images/{name}_{timestamp}.jpg"
        
        data['image'] = fileName
        
        employee_data = {}
        try:
            with open('employee_data.json', 'r') as f:
                employee_data = json.load(f)
        except Exception as e:
            print(f"Error: {e}")
            

        if date not in employee_data:
            employee_data[date] = []

        last_entry = None
        # check the list in reverse order
        for entry in reversed(employee_data[date]):
            if entry['name'] == name:
                last_entry = entry
                break
        
        if last_entry is not None:
            lastTime = time.mktime(time.strptime(last_entry['timestamp'], "%Y-%m-%d %H:%M:%S"))
            currentTime = time.mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
            wt_for_duplicate = 1
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    wt_for_duplicate = settings['wt_for_duplicate'] # time in seconds
                    # if wt_for_duplicate is number else 0
                    wt_for_duplicate = wt_for_duplicate if wt_for_duplicate else 0
            except Exception as e:
                print(f"Error: {e}")
            if currentTime - lastTime < wt_for_duplicate:
                print(f"{name} has already registered for {entry_type} at {last_entry['timestamp']}")
                return

        employee_data[date].append(data)
        try:
            with open('employee_data.json', 'w') as f:
                json.dump(employee_data, f, indent=4)
        except Exception as e:
            print(f"Error: {e}")

        print(f"Registered {name} for {entry_type} at {timestamp}")




def sync_data_to_server():
    synced = SyncDataToServer()
    sync_thread = threading.Thread(target=synced.run)
    sync_thread.start()


if __name__ == "__main__":
    thread = threading.Thread(target=sync_data_to_server)
    thread.start()
    
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()