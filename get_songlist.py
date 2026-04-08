import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


genre_cache = {}

def get_artist_genres(artist_name):
    # 1. Check if we already know this artist
    if artist_name in genre_cache:
        return genre_cache[artist_name]

    try:
        results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        items = results['artists']['items']
        genres = items[0].get('genres', [])[:2] if items else []
        
        # 2. Save to cache so we don't hit the API again for this person
        genre_cache[artist_name] = genres
        return genres
    except Exception as e:
        # If we hit a rate limit (429), Spotipy usually handles the wait, 
        # but returning an empty list keeps the app from crashing.
        print(f"Error for {artist_name}: {e}")
        return []

def get_artist_URL(artist_name):
    """Returns the Spotify URL for an artist."""
    results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
    items = results['artists']['items']
    if not items:
        return -1
    return items[0]['external_urls']['spotify']

def get_artist_tracks(artist_URL):
    """Returns top track names."""
    if artist_URL == -1:
        return []
    try:
        top_tracks = sp.artist_top_tracks(artist_URL, country='US')
        return [track['name'] for track in top_tracks['tracks']]
    except Exception as e:
        print(f"Error fetching tracks: {e}")
        return []

def get_artist_list(artist_names):
    """Original function for the AJAX route to fetch songs."""
    artist_map = {}
    for name in artist_names:
        url = get_artist_URL(name)
        tracks = get_artist_tracks(url)
        artist_map[name] = tracks
    return artist_map