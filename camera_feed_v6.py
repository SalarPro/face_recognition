import threading
import time
import asyncio

class SyncDataToServer:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    async def sync(self):
        while True:
            print("Syncing data to server...")
            await asyncio.sleep(5)  # Simulate a network operation
            print("Data synced to server.")

    def run(self):
        self.loop.run_until_complete(self.sync())

def sync_data_to_server():
    syncer = SyncDataToServer()
    syncer.run()

def main():
    # Start the sync data to server thread
    thread = threading.Thread(target=sync_data_to_server)
    thread.start()
    
    # Your main code here
    print("Main code running...")
    while True:
        time.sleep(1)
        print("Main code running...")
        
if __name__ == "__main__":
    main()