import json
import os
import time
import asyncio
import requests
import Database as db

class SyncDataToServer:
    
    setting_path = 'settings.json'
    face_encodings_path = 'face_data/face_encodings.pkl'
    user_images_queue_path = '../user_images_queue'
    face_cascade_path = 'face_data/haarcascade_frontalface_default.xml'
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        

    async def sync(self):
        # runSeconds = [15, 30, 45, 0]
        runSeconds = [0, 30]
        while True:
            if time.localtime().tm_sec in runSeconds:
                self.calculate_data()
            await asyncio.sleep(1)
            
    def run(self):
        self.loop.run_until_complete(self.sync())
    
    def calculate_data(self):
        print("Calculating data")
        self.db = db.Database()
        print("Database created v2")
        # read settings.json to get sync_to_server value it is a boolean value
        sync_to_server = False
        try:
            with open(self.setting_path, 'r') as f:
                settings = json.load(f)
                sync_to_server = settings['sync_to_server']
        except Exception as e:
            print(f"Error: {e}")
        
        if not sync_to_server:
            print("Sync to server is disabled")
            return
        
        print("Sync to server is enabled")
        unsent_entries = self.db.get_all_unsent()
        print(f"Unsent entries: {unsent_entries}")
        
        
        
        for entry in unsent_entries:
            response = self.send_data_to_server(entry)
            # if the response is string
            if isinstance(response, str):
                self.db.update_server_response(entry[0], response, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                continue
            try:
                if(response.get('status') == 'success'):
                    self.db.delete(entry[0])
                    continue
            except Exception as e:
                print(f"Error: {e}")
        
        self.db.close()

    def send_data_to_server(self, data):

        dId = data[0]
        dUserId = data[1]
        dName = data[2]
        dTime = data[3]
        dType = data[4]
        dPercentage = data[5]
        dImage = data[6]
        dSentToServer = data[7]
        dServerResponse = data[8]
        
        
        api_prefix = "http://kavin.test/api/v1/"
        apiKey = ""
        try:
            with open(self.setting_path, 'r') as f:
                settings = json.load(f)
                api_prefix = settings['api_prefix']
                apiKey = settings['api_key']
        except Exception as e:
            print(f"Error: {e}")
        
        url = api_prefix + "entry"
        
        files = {}
        imageName = dImage
        if imageName:
            isFileExist = os.path.isfile(imageName)
            if isFileExist:
                openFile = open(imageName, 'rb')
                files = {'image': openFile}
        
        nData = {
            'id': dId,
            'user_id': dUserId,
            'name': dName,
            'timestamp': dTime,
            'type': dType,
            'percentage': dPercentage,
            'sent_to_server': dSentToServer,
            'server_response': dServerResponse
        }
        nData['api_key'] = apiKey
        try:
            response = requests.post(url, files=files, data=nData)
            response.raise_for_status()
            resp = response.json()
            if resp['status'] == 'success':
                if os.path.exists(imageName):
                    openFile.close()
                    os.remove(imageName)
            print(f"Response: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error123 sending data to server: {e}")
            return str(e)
