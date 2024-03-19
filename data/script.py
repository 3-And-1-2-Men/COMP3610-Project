import pandas as pd
import requests
import time

from os import path
from random import randint
from timeit import default_timer as timer

auth_url = "https://accounts.spotify.com/api/token"
response = requests.post(auth_url, {
    "grant_type": "client_credentials",
    "client_id": "24432fee68ea464c94ed2eeaff451fea",
    "client_secret": "5a4e797fab984adb9375ee8c6b9fab95"
})
api_token = response.json()['access_token']
print("API Response Status:", response.status_code, "\nToken:", api_token)

folder_path = path.expanduser("~") + path.sep + path.sep.join(["Onedrive", "Desktop", "COMP3610-Project", "data"])
data = pd.read_csv(folder_path + path.sep + "spotify_master.csv")

url = "https://api.spotify.com/v1/audio-analysis/"
headers = {
    "Authorization": f"Bearer {api_token}"
}

end, start = len(data), int(len(data)/2) - 1
num_404, num_ok = 0, 0
new_data_filename = folder_path + path.sep + f"spotfiy_tracks_timbre_2.csv"
file_header = "id,status,timbre"
with open(new_data_filename, "a+", encoding="utf-8") as f:
    header = f.readline().strip()
    if header != file_header: f.write(file_header)

# Stats
print(f"Start: {start}")
print(f"End: {end}")
print(f"Data Dump File: '{new_data_filename}'")

# Find last row in file
def get_resume_idx(start = 0):
    start, last_line = start, None
    with open(new_data_filename, "r", encoding="utf-8") as f:
        last_line = f.readlines()[-1]
        
    if last_line != file_header:
        id = last_line.split(",")[0]
        start = data[data["id"] == id].index[0] + 1
    
    return start

print(f"Fast track: {get_resume_idx(start)}")
data.iloc[get_resume_idx(start)]

def format_time(x: float) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(x))

def log_msg(idx, end, elapsed, response, num_ok, num_404, cooldown = None):
    print(f"\r[{idx + 1}/{end}] Elapsed: {format_time(elapsed)} | Status: {response.status_code} | OK: {num_ok} | 404: {num_404} {' | COOLDOWN: ' + format_time(cooldown) if cooldown else ''}" + " " * 9, end="")

_timer = time.time()
idx = get_resume_idx(start)

while idx < end:
    response = requests.get(f"{url}{data.iloc[idx]['id']}", headers=headers)
    num_404 += 1 if response.status_code == 404 else 0
    num_ok  += 1 if response.status_code == 200 else 0
    elapsed  = time.time() - _timer
    log_msg(idx, end, elapsed, response, num_ok, num_404)
    
    # Generate random cooldown time (2 - 3 hours) in seconds
    if response.status_code == 429:
        hour_secs = 60 * 60
        cooldown = randint(2 * hour_secs, 3 * hour_secs)
        while cooldown > 0:
            log_msg(idx, end, elapsed, response, num_ok, num_404, cooldown)
            time.sleep(1)
            cooldown, elapsed = cooldown - 1, time.time() - _timer
            
        continue # Retry from last row
    
    # Get data and write to file
    id, status = data["id"].iloc[idx], response.status_code
    timbre = response.json()["segments"][0]["pitches"] if response.status_code == 200 else 0
    with open(new_data_filename, "a", encoding="utf-8") as f: f.write(f"\n{id},{status},\"{timbre}\"")
    
    # Generate random sleep time (2 - 5 secs)
    cooldown = randint(2, 5)
    while cooldown > 0:
        log_msg(idx, end, elapsed, response, num_ok, num_404, cooldown)
        time.sleep(1)
        cooldown, elapsed = cooldown - 1, time.time() - _timer
    
    idx += 1

print(f"Number of tracks that returned a 404 status: {num_404}")