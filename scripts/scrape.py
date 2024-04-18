import pandas as pd
import requests
import time
from os import path
from random import randint

# Globals
folder_path     = __file__.split("scripts")[0] + "data" + path.sep
filename        = folder_path + f"spotify_tracks_timbre.csv"
file_header     = "id,status,timbre"
data            = pd.read_csv(folder_path + "spotify_master.csv")
auth_url        = "https://accounts.spotify.com/api/token"
data_url        = "https://api.spotify.com/v1/audio-analysis/"
request_headers = { "Authorization": f"Bearer" }

# Authenticate with Spotify API to get access token
def authenticate():
    response = requests.post(auth_url, {
        "grant_type": "client_credentials",
        "client_id": "",        # your spotify developer app client id
        "client_secret": ""     # your spotify developer app client secret
    })
    api_token = response.json()['access_token']
    if response.status_code == 200:
        request_headers["Authorization"] = f"Bearer {api_token}"
        print("Spotify Web API authentication successful")

authenticate()


# Setup for data scraping
end, start = len(data), int(len(data)/2) + 1
num_404, num_ok = 0, 0
print(f"Index Range: {start} ==> {end}")
print(f"Data Dump File: '{filename}'")

# Create new data dump file if it doesn't exist
if not path.exists(filename):
    with open(filename, "w", encoding="utf-8") as f: f.write(file_header + "\n")

# Find last row in file
def get_resume_idx(start: int = 0) -> int:
    start, last_line = start, None
    with open(filename, "r", encoding="utf-8") as f: last_line = f.readlines()[-1]
    if last_line == file_header: return start
    id = last_line.split(",")[0]
    start = data[data["id"] == id].index[0] + 1
    return start

print(f"Fast track: {get_resume_idx(start)}")
data.iloc[get_resume_idx(start)]

def format_time(x: float) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(x))

def log_msg(idx, end, elapsed, response, num_ok, num_404, cooldown = None, fetch = False) -> None:
    print(f"\r[{idx + 1}/{end}] Elapsed: {format_time(elapsed)} | Status: {response.status_code if response else 'XXX'} | OK: {num_ok} | 404: {num_404}{' | COOLDOWN: ' + format_time(cooldown) if cooldown else ''}{' | FETCHING ...' if fetch else ''}" + " " * 15, end="")

_timer = time.time()
idx = get_resume_idx(start)

response = None
reconnect_delay = 10
while idx < end:
    elapsed  = time.time() - _timer
    try:
        log_msg(idx, end, elapsed, response, num_ok, num_404, fetch = True)
        response = requests.get(f"{data_url}{data.iloc[idx]['id']}", headers=request_headers)
        
    except Exception as e:
        if "Connection" in str(e):
            print(f"\nError => {e}.\nReconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)
            continue
        
    num_404 += 1 if response.status_code == 404 else 0
    num_ok  += 1 if response.status_code == 200 else 0
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
    
    if response.status_code == 401:
        print("\nError: 401 Unauthorized. Re-running authentication procedure...")
        authenticate()
        continue # Retry from last row
    
    # Get data and write to file
    id, status = data["id"].iloc[idx], response.status_code
    timbre = response.json()["segments"][0]["pitches"] if response.status_code == 200 else 0
    with open(filename, "a", encoding="utf-8") as f: f.write(f"\n{id},{status},\"{timbre}\"")
    
    # Generate random sleep time (2 - 5 secs)
    cooldown = randint(2, 3)
    while cooldown > 0:
        log_msg(idx, end, elapsed, response, num_ok, num_404, cooldown)
        time.sleep(1)
        cooldown, elapsed = cooldown - 1, time.time() - _timer
    
    idx += 1
    while data.iloc[idx]['key'] <= 0: idx += 1

print(f"\nSpotify data scraping complete")