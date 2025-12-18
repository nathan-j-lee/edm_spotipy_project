import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# This looks for a .env file in the same directory and loads it
load_dotenv()

# This automatically looks for the environment variables we set
scope = "user-library-read"

# authenticate Spotify based on the scope above
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# Test it
results = sp.current_user_saved_tracks(limit=1)
print("Successfully connected to Spotify!")

# Test out artist_top_tracks() method
olivia_dean_url = 'https://open.spotify.com/artist/00x1fYSGhdqScXBRpSj3DW'
# results is giant JSON blob, need to sift through it and get the info we need
results = sp.artist_top_tracks(olivia_dean_url, country='US')

track_names = [track['name'] for track in results['tracks']]
for name in track_names:
    print(name)


# Search for an artist's name and return their external URL
def get_artist_URL(artist_name):
    results = sp.search(q=f'{artist_name}', type='artist', limit=1)
    results_items = results['artists']['items']
    if len(results_items) < 1:
        print("artist not found")
    else:
        artist = results_items[0]
        return artist['external_urls']['spotify']

sp_search = input("Search: ")
print(get_artist_URL(sp_search))