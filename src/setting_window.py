import tkinter as tk
from tkinter import messagebox
import json
from tkinter import PhotoImage

class SettingsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Settings")
        self.root.attributes("-topmost", True)  # Make the window always on top
        icon = PhotoImage(file="ico.png")
        self.root.iconphoto(True, icon)
        self.root.geometry("700x400+{}+{}".format(int(self.root.winfo_screenwidth()/2 - 250), int(self.root.winfo_screenheight()/2 - 250)))
        self.root.minsize(300, 400)

        self.settings = self.load_settings()

        tk.Label(root, text="WT for Duplicate").grid(row=0, column=0, sticky='e')
        self.wt_for_duplicate_entry = tk.Entry(root, width=50)
        self.wt_for_duplicate_entry.grid(row=0, column=1, sticky='ew')
        self.wt_for_duplicate_entry.insert(0, self.settings["wt_for_duplicate"])

        tk.Label(root, text="WT for Each Frame").grid(row=1, column=0, sticky='e')
        self.wt_for_each_frame_entry = tk.Entry(root, width=50)
        self.wt_for_each_frame_entry.grid(row=1, column=1, sticky='ew')
        self.wt_for_each_frame_entry.insert(0, self.settings["wt_for_each_frame"])

        tk.Label(root, text="Camera ID Exit").grid(row=2, column=0, sticky='e')
        self.camera_id_exit_entry = tk.Entry(root, width=50)
        self.camera_id_exit_entry.grid(row=2, column=1, sticky='ew')
        self.camera_id_exit_entry.insert(0, self.settings["camera_id_exit"])

        tk.Label(root, text="Camera ID Enter").grid(row=3, column=0, sticky='e')
        self.camera_id_enter_entry = tk.Entry(root, width=50)
        self.camera_id_enter_entry.grid(row=3, column=1, sticky='ew')
        self.camera_id_enter_entry.insert(0, self.settings["camera_id_enter"])

        tk.Label(root, text="Accepted Percentage").grid(row=4, column=0, sticky='e')
        self.accepted_percentage_entry = tk.Entry(root, width=50)
        self.accepted_percentage_entry.grid(row=4, column=1, sticky='ew')
        self.accepted_percentage_entry.insert(0, self.settings["accepted_percentage"])

        tk.Label(root, text="Token").grid(row=5, column=0, sticky='e')
        self.token_entry = tk.Entry(root, width=50)
        self.token_entry.grid(row=5, column=1, sticky='ew')
        self.token_entry.insert(0, self.settings["token"])

        tk.Label(root, text="API Key").grid(row=6, column=0, sticky='e')
        self.api_key_entry = tk.Entry(root, width=50)
        self.api_key_entry.grid(row=6, column=1, sticky='ew')
        self.api_key_entry.insert(0, self.settings["api_key"])

        tk.Label(root, text="API Secret").grid(row=7, column=0, sticky='e')
        self.api_secret_entry = tk.Entry(root, width=50)
        self.api_secret_entry.grid(row=7, column=1, sticky='ew')
        self.api_secret_entry.insert(0, self.settings["api_secret"])

        tk.Label(root, text="API Prefix").grid(row=8, column=0, sticky='e')
        self.api_prefix_entry = tk.Entry(root, width=50)
        self.api_prefix_entry.grid(row=8, column=1, sticky='ew')
        self.api_prefix_entry.insert(0, self.settings["api_prefix"])

        tk.Label(root, text="API URL Save User Attendance").grid(row=9, column=0, sticky='e')
        self.api_url_save_user_attendance_entry = tk.Entry(root, width=50)
        self.api_url_save_user_attendance_entry.grid(row=9, column=1, sticky='ew')
        self.api_url_save_user_attendance_entry.insert(0, self.settings["api_url_save_user_attendance"])

        tk.Label(root, text="API URL Update Face Encoding").grid(row=10, column=0, sticky='e')
        self.api_url_update_face_encoding_entry = tk.Entry(root, width=50)
        self.api_url_update_face_encoding_entry.grid(row=10, column=1, sticky='ew')
        self.api_url_update_face_encoding_entry.insert(0, self.settings["api_url_update_face_encoding"])

        tk.Label(root, text="Sync Interval").grid(row=11, column=0, sticky='e')
        self.sync_interval_entry = tk.Entry(root, width=50)
        self.sync_interval_entry.grid(row=11, column=1, sticky='ew')
        self.sync_interval_entry.insert(0, self.settings["sync_interval"])

        tk.Label(root, text="Sync to Server").grid(row=12, column=0, sticky='e')
        self.sync_to_server_var = tk.BooleanVar(value=self.settings["sync_to_server"])
        self.sync_to_server_checkbutton = tk.Checkbutton(root, variable=self.sync_to_server_var)
        self.sync_to_server_checkbutton.grid(row=12, column=1, sticky='w')

        # Add save button
        save_button = tk.Button(root, text="Save", command=self.update_settings)
        save_button.grid(row=13, column=0, columnspan=2, sticky='e', padx=10, pady=10)

        # Make the columns expand with the window
        root.grid_columnconfigure(1, weight=1)

    def load_settings(self):
        with open('settings.json', 'r') as file:
            return json.load(file)

    def save_settings(self, settings):
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)

    def update_settings(self):
        self.settings["wt_for_duplicate"] = float(self.wt_for_duplicate_entry.get())
        self.settings["wt_for_each_frame"] = float(self.wt_for_each_frame_entry.get())
        self.settings["camera_id_exit"] = int(self.camera_id_exit_entry.get())
        self.settings["camera_id_enter"] = int(self.camera_id_enter_entry.get())
        self.settings["accepted_percentage"] = int(self.accepted_percentage_entry.get())
        self.settings["token"] = self.token_entry.get()
        self.settings["api_key"] = self.api_key_entry.get()
        self.settings["api_secret"] = self.api_secret_entry.get()
        self.settings["api_prefix"] = self.api_prefix_entry.get()
        self.settings["api_url_save_user_attendance"] = self.api_url_save_user_attendance_entry.get()
        self.settings["api_url_update_face_encoding"] = self.api_url_update_face_encoding_entry.get()
        self.settings["sync_interval"] = int(self.sync_interval_entry.get())
        self.settings["sync_to_server"] = self.sync_to_server_var.get()
        self.save_settings(self.settings)
        # messagebox.showinfo("Info", "Settings saved successfully", parent=self.root)
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# Example usage:
# from setting_window import SettingsWindow
# settings_window = tk.Toplevel(self.root)
# app = SettingsWindow(settings_window)
# app.run()