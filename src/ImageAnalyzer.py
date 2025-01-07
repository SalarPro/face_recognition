import os
import cv2
import face_recognition
import json
import time
import pickle
import Database as db
import asyncio
import datetime

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
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    async def sync(self):
        # runSeconds = [15, 45]
        runSeconds = [7 , 22, 37, 52]
        while True:
            # if time.localtime().tm_sec % 5 == 0:
            self.start()
            await asyncio.sleep(1)
            
    def run(self):
        self.loop.run_until_complete(self.sync())

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
            print(f"Error[58416]: {e}")
            return 80

    def compare_faces(self, image_path):
        try:
            # if image file start with done_ then return
            if image_path.split('\\')[-1].startswith('done_'):
                return "Unknown", -1
            
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error[8416]: Could not read image {image_path}")
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
        except Exception as e:
            print(f"Error[6543]: {e}")
            return "Unknown", -1
        return "Unknown", 0

    def record_attendee(self, name, percentage, image_path):
        try:
            # filePahtName
            # (i|o)I(time).jpg
            # ex: i_1735393560.4280732.jpg
            # image path start with i or o, i is for in and o is for out
            # print(image_path) # ./user_images_queue\i_1735402052.2187057.jpg
            fileName = image_path.split('\\')[-1]
            type = fileName[0]
            timeStr = fileName.split('_')[1].split('.')[0]

            if type == 'i':
                type = 'in'
            elif type == 'o':
                type = 'out'
            else:
                os.remove(image_path)
                return
            
            # rename image file add done to the beginning of the file name
            try:
                os.rename(image_path, f"./user_images_queue/done_{fileName}")
            except Exception as e:
                print(f"Error[85756] renaming file {image_path}: {e}")
                return
            image_path = f"./user_images_queue/done_{fileName}"
            
            # timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(timeStr)))
            # date = time.strftime("%Y-%m-%d", time.localtime())
            # data = {
            #     "name": name,
            #     "timestamp": timestamp,
            #     "percentage": percentage,
            #     "image": image_path,
            #     "sent_to_server": False,
            #     "server_response": None,
            #     "type": type
            # }
            # name start with number_string
            userId = name.split('_')[0]
            userName = name.split('_')[1]

            isSaved = True
            try:
                timeStamp2 = datetime.datetime.fromtimestamp(float(timeStr))
                isSaved = self.db.insertV2(userId, userName, timestamp, percentage, image_path, 0, None, type, None, timeStamp2)
            except Exception as e:
                print(f"Error[54611111]: {e}")
                self.db.insert(userId, userName, timestamp, percentage, image_path, 0, None, type, None)
                isSaved = True

            if not isSaved:
                print(f"is already recorded {name} {percentage:.2f}% at {timestamp}")
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error[999925] deleting {image_path}: {e}")
                return
            print(f"[4452]Recorded {name} with {percentage:.2f}% similarity at {timestamp}")
        except Exception as e:
            print(f"Error[777_45]: {e}")
        

    def start(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("==========ImageAnalyzer started===========")
            self.db = db.Database()
                
            if not os.path.exists(self.user_images_queue_path):
                print(f"Error[8441140]: The directory {self.user_images_queue_path} does not exist.")
                return
            count = 0
            for image_file in os.listdir(self.user_images_queue_path):
                image_path = os.path.join(self.user_images_queue_path, image_file)
                if os.path.isfile(image_path) and image_file.endswith('.jpg') and not image_file.startswith('done_'):
                    name, percentage = self.compare_faces(image_path)
                    # print(count, name, percentage)
                    count += 1
                    if name != "Unknown":
                        self.record_attendee(name, percentage, image_path)
                    elif percentage != -1:
                        try:
                            os.remove(image_path)
                        except Exception as e:
                            print(f"Error[75244]: {e}")
            self.db.close()
            print("##########ImageAnalyzer stopped##########")
            # clear the terminal
        except Exception as e:
            print(f"Error[84117]: {e}")
            try:
                self.db.close()
            except Exception as e:
                print(f"Error[84133]: {e}")
            print("ImageAnalyzer stopped")
# if __name__ == "__main__":
#     analyzer = ImageAnalyzer('face_data/face_encodings.pkl', 'settings.json', 'user_images_queue')
#     analyzer.start()
