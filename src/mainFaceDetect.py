import tkinter as tk
from tkinter import ttk
import threading
from tkinter import PhotoImage
from ImageAnalyzer import ImageAnalyzer
import os



camera_id_exit = 0
camera_id_enter = 1

print("Loading... Face Detection Server")

class FaceRecognitionAppServer:
    
    setting_path = 'settings.json'
    employee_data_path = 'attendee/employee_data.json'
    face_encodings_path = 'face_data/face_encodings.pkl'
    user_images_queue_path = '../user_images_queue'
    face_cascade_path = 'face_data/haarcascade_frontalface_default.xml'
    
    def __init__(self, root):
        self.root = root
        self.root.title("Kavin | Face Recognition")
        self.root.attributes("-topmost", True)  # Make the window always on top
        icon = PhotoImage(file="ico.png")
        self.root.iconphoto(True, icon)
        
        # # override the close button to call the exit_the_app function
        self.root.protocol("WM_DELETE_WINDOW", self.exit_the_app) 
        
        # # Create GUI elements
        self.create_widgets()

    
    def create_widgets(self):
        
        # add large text "Server is working and ready to go" in the center of the screen
        self.lbl1 = ttk.Label(self.root, text="Face are detecting. Dont close.", font=("Arial Bold", 30))
        self.lbl1.grid(row=0, column=0, padx=10, pady=50)

        
    def exit_the_app(self):
        print("Exiting the app...🤑")
        # self.root.destroy()
        # end all process inclooding the sync_data_to_server and the camera threads and queues
        self.root.quit()
        self.root.destroy()
        os._exit(0)


def start_face_detection():
    synced = ImageAnalyzer()
    sync_thread = threading.Thread(target=synced.run)
    sync_thread.start()


if __name__ == "__main__":
    thread = threading.Thread(target=start_face_detection)
    thread.start()
    
    root = tk.Tk()
    app = FaceRecognitionAppServer(root)
    root.mainloop()