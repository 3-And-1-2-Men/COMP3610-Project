from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.models import db
from App.controllers import create_user

import os
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

index_views = Blueprint('index_views', __name__, template_folder='../templates')

emotions_map = {
    "Calm":        ["relief"],
    "Energetic":   ["excitement"],
    "Frantic":     ["fear"],
    "Exuberant":   ["amusement"],
    "Happy":       ["joy"],
    "Sad":         ["sadness"],
    "Depression":  ["grief", "remorse"],
    "Contentment": ["gratitude"]
}

def label_to_emotion(label: int) -> str:
    x = list(emotions_map.keys())[label]
    return str(x)[0].upper() + x[1:]

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

@index_views.route('/init', methods=['GET'])
def init():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
    return jsonify(message='db initialized!')

@index_views.route('/get-emotion', methods=['POST'])
def get_emotion():
    text = request.json['text']
    print("Predicting on text: ", text)
    # model = load_model(os.path.dirname(__file__).split("App")[0] + "models" + os.sep + "emotion_detection_62_precision.keras")
    
    # Get predicted emotion
    # tokenizer = Tokenizer()
    # test_seq = tokenizer.texts_to_sequences(text)
    # test_padded_seq = pad_sequences(test_seq, maxlen=30)
    # model_prediction = model.predict(test_padded_seq)
    # emotion = label_to_emotion(np.argmax(model_prediction[0]))
    emotion = "Happy"
    print("Detected emotion: ", emotion)
    
    # Load classified list of songs
    music_data = pd.read_csv(os.path.dirname(__file__).split("App")[0] + "data" + os.sep + "classified_spotify_data.csv")
    shuffled_songs = music_data[music_data['mood'] == emotion].sample(frac=1).reset_index(drop=True)
    candidates = shuffled_songs.head(100)
    
    # Authenticate with Spotify
    cid = os.environ.get('SPOTIPY_CLIENT_ID')
    secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
    print("Using client ID: ", cid)
    print("Using client secret: ", secret)
    spotify = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-public",
            username="f3k2otvg6cfm9i5p4qygfvqol",
            client_id=cid,
            client_secret=secret,
            redirect_uri="http://localhost:8888/callback"
        )
    )
    user = spotify.current_user()
    user_id = user['id']
    
    # Create playlist
    # Create new playlist
    playlist_name = emotion + " Songs"
    playlist = spotify.user_playlist_create(user=user_id, name=playlist_name)
    playlist_id = playlist['id']

    # Add tracks to playlist
    track_ids = candidates['id'].tolist()
    spotify.playlist_add_items(playlist_id=playlist_id, items=track_ids)

    # Get link to playlist
    playlist_link = f"https://open.spotify.com/playlist/{playlist_id}"
    print("Playlist link: ", playlist_link)
    
    return {
        'emotion': emotion,
        'playlist_link': playlist_link
    }
    
@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})