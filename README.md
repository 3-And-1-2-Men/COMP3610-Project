# COMP3610-Project

[![Open In Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/googlecolab/colabtools/blob/main/COMP3610-GroupA.ipynb)

## Datasets Used
- [Spotify 1.2M Dataset](https://www.kaggle.com/datasets/rodolfofigueroa/spotify-12m-songs)
- [Google Emotions Dataset](https://www.kaggle.com/datasets/shivamb/go-emotions-google-emotions-dataset)

## Instructions

1. In order to run this program, you will need a Spotify Developer App. You can find instructions on how to setup this developer app [here](https://www.codeproject.com/Tips/5276627/HowTo-Setup-a-Spotify-API-App-in-the-Spotify-Devel). Using your Spotify Developer app, retrieve the following from your application by navigating to its Settings page:
  - Client ID
  - Client Secret (look carefully as it is hidden at first, not immediately visible)

2. After setting up your Spotify Developer App and retrieving your Client ID and Secret, you'll need to store the keys into an `.env` file.<br>
   For security purposes, **DO NOT HARDCODE THESE VALUES** into your local installation. If these keys reach a public github repository, they will be scraped and abused.<br><br>
   The structure of your `.env` file should be as follows:
  ```
  SPOTIPY_CLIENT_ID=YOUR_CLIENT_ID
  SPOTIPY_CLIENT_SECRET=YOUR_CLIENT_SECRET
  ```

3. Install the following packages as listed in the [requirements.txt](https://github.com/3-And-1-2-Men/COMP3610-Project/blob/main/requirements.txt) (needed to fun Flask Web Application)

4. If you've reached this point, simply run the following commands
  ```
  flask init
  flask run
  ```
  The server should automatically start up on your localhost and should be reachable at `localhost:8080`
