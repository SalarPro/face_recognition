import json
import os
import time
import asyncio
import requests
import cv2
from encode_faces import EncodeFaces

class LoadUserData:
    
    setting_path = 'settings.json'
    face_encodings_path = 'face_data/face_encodings.pkl'
    user_images_queue_path = '../user_images_queue'
    user_images_faces_path = './known_faces2'
    face_cascade_path = 'face_data/haarcascade_frontalface_default.xml'
    apiKey = ""
    api_prefix = "http://kavin.test/api/v1/"
    users = []
    
    def __init__(self):
        self.data = {}
        try:
            with open(self.setting_path, 'r') as f:
                settings = json.load(f)
                self.api_prefix = settings['api_prefix']
                self.apiKey = settings['api_key']
        except Exception as e:
            print(f"Error: {e}")

    def start(self):
        url = self.api_prefix + "userData"
        print(f"url: {url}")
        nData = {
            "api_key": self.apiKey,
        }
        print(f"Data: {nData}")
        try:
            response = requests.get(url,nData)
            response.raise_for_status()
            response = response.json()
            print(f"Response: {response}")
        except requests.exceptions.RequestException as e:
            print(f"Error123 sending data to server: {e}")
            return str(e)
        
        print(f"start function {response['status']}")
        if response['status'] == 'success':
            print("status is success")
            self.users = response['users']
            self.loadUserImage(self.users)
            
        
        enFace = EncodeFaces()
        enFace.encode_faces()
        
        print("start function end")

    def loadUserImage(self, users):
        print("loadUserImage function")
        # if self.user_images_faces_path does not exist, create it
        if not os.path.exists(self.user_images_faces_path):
            os.makedirs(self.user_images_faces_path)
            print(f"Directory {self.user_images_faces_path} created")
        # delete all files in the user_images_faces_path
        files = os.listdir(self.user_images_faces_path)
        for file in files:
            os.remove(f"{self.user_images_faces_path}/{file}")
            
        for user in users:
            userId = user['id']
            userName = user['name']
            idName = user['idName']
            userImage = user['image']
            imgPath = self.downloadImage(userImage, idName)
            self.enhanceImage(imgPath, idName)
            
    def downloadImage(self, url, idName):
        try:
            response = requests.get(url)
            print(f"Downloading image {response.status_code}")
            if response.status_code == 200:
                imgPath = f"{self.user_images_faces_path}/{idName}.jpg"
                print(f"Image path: {imgPath}")
                with open(imgPath, 'wb') as f:
                    f.write(response.content)
                    return imgPath
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def enhanceImage(self, imgPath, idName):
        # detect face in the image
        # zoom in the face {crop the face}
        # using cv2
        face_cascade = cv2.CascadeClassifier(self.face_cascade_path)
        img = cv2.imread(imgPath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            padding = 50
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(img.shape[1], x + w + padding)
            y2 = min(img.shape[0], y + h + padding)
            roi_color = img[y1:y2, x1:x2]
            cv2.imwrite(imgPath, roi_color)
        return imgPath
