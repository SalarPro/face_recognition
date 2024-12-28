import json
import os
import time
import asyncio
import requests

class SyncDataToServer:
    
    setting_path = 'settings.json'
    employee_data_path = 'attendee/employee_data.json'
    face_encodings_path = 'face_data/face_encodings.pkl'
    user_images_queue_path = '../user_images_queue'
    face_cascade_path = 'face_data/haarcascade_frontalface_default.xml'
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def sync(self):
        while True:
            if time.localtime().tm_sec == 0:
                self.calculate_data()
            # await asyncio.sleep(1)
            
    def run(self):
        self.loop.run_until_complete(self.sync())
    
    def calculate_data(self):

        # read settings.json to get sync_to_server value it is a boolean value
        sync_to_server = False
        try:
            with open(self.setting_path, 'r') as f:
                settings = json.load(f)
                sync_to_server = settings['sync_to_server']
        except Exception as e:
            print(f"Error: {e}")
        
        if not sync_to_server:
            return
        
        with open(self.employee_data_path, 'r') as f:
            employee_data = json.load(f)
        
        for date, entries in employee_data.items():
            for entry in entries:
                if not entry['sent_to_server']:
                    # Send the data to the server
                    response = self.send_data_to_server(entry)
                    # if the response is string
                    if isinstance(response, str):
                        entry['sent_to_server'] = False
                        entry['server_response'] = response
                        continue
                    try:
                        if(response.get('status') == 'success'):
                            entry['sent_to_server'] = True
                        else:
                            entry['sent_to_server'] = False
                    except Exception as e:
                        print(f"Error: {e}")
                    entry['server_response'] = response
                    entry['sent_to_server_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        with open(self.employee_data_path, 'w') as f:
            json.dump(employee_data, f, indent=4)


    def send_data_to_server(self, data):
        # Simulate sending data to server
        print(f"Sending data to server: {data}")
        # load api_prefix from settings.json
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
        print(f"url: {url}")
        

        files = {}
        imageName = data['image'] 
        if imageName:
            isFileExist = os.path.isfile(imageName)
            if isFileExist:
                files = {'image': open(imageName, 'rb')}
        
        nData = data.copy()
        nData['api_key'] = apiKey
        try:
            response = requests.post(url, files=files, data=nData)
            response.raise_for_status()
            resp = response.json()
            if resp['status'] == 'success' and imageName and os.path.isfile(imageName):
                os.remove(imageName)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error123 sending data to server: {e}")
            return str(e)
