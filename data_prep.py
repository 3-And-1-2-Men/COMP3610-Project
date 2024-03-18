import pandas as pd
import requests
from os import path

auth_url = "https://accounts.spotify.com/api/token"
response = requests.post(auth_url, {
    "grant_type": "client_credentials",
    "client_id": "24432fee68ea464c94ed2eeaff451fea",
    "client_secret": "5a4e797fab984adb9375ee8c6b9fab95"
})
api_token = response.json()['access_token']
print("API Response Status:", response.status_code, "\nToken:", api_token)

data = pd.read_csv(path.expanduser("~") + path.sep + path.sep.join(["Downloads", "tracks_features.csv"]))
data = data.drop(columns=["instrumentalness","liveness","time_signature","year","release_date","album_id","album","artist_ids","track_number","disc_number","explicit","danceability","acousticness","duration_ms","artists","mode","loudness","speechiness","valence"])
url = "https://api.spotify.com/v1/audio-analysis/"
headers = { "Authorization": f"Bearer {api_token}" }
num_tracks = len(data)
end = 802683
start = end - 220000
print(f"Number of tracks: {num_tracks}")
num_404, num_ok = 0, 0
new_data_filename = path.expanduser("~") + path.sep + path.sep.join(["Downloads", "test.csv"])
with open(new_data_filename, "w", encoding="utf-8") as f: f.write("id,status,timbre")

# Stats
print(f"Start: {start}")
print(f"End: {end}")

for i in range(start, end + 1):
    response = requests.get(f"{url}{data.iloc[i]["id"]}", headers=headers)
    num_404 += 1 if response.status_code != 200 else 0
    num_ok += 1 if response.status_code == 200 else 0
    print(f"\r[{i}/{end}] Status: {response.status_code} | OK: {num_ok} | 404: {num_404}" + " " * 15, end="")
    id = data["id"].iloc[i]
    status = response.status_code
    timbre = response.json()["segments"][0]["pitches"] if response.status_code == 200 else 0
    with open(new_data_filename, "a", encoding="utf-8") as f: f.write(f"\n{id},{status},\"{timbre}\"")

print(f"Number of tracks that returned a 404 status: {num_404}")