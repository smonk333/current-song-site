import requests
import time

# change everything before '/song-update' to match your domain
URL = "http://localhost:5000/song-update"

# change this to the path of the file you want to monitor
FILE_PATH = "C:/Users/username/nowplaying.txt"

# set how often the script will monitor the file for changes
INTERVAL = 5 # check every 5 seconds

# store the last read track info (to see if we need to update)
last_track = None

while True:
    try:
        with open(FILE_PATH, "r") as file:
            current_track = file.read().strip()

        # if the track info has changed, send a request to the server
        if current_track != last_track:
            payload = {"track": current_track}
            response = requests.post(URL, json=payload)

            # check if the request was successful
            if response.status_code == 200:
                print(f"Sent track info: {current_track}")
            else:
                print(f"Failed to send track info: {response.status_code}")

            last_track = current_track

    except Exception as e:
        print(f"An error occurred: {e}")

    time.sleep(INTERVAL)
