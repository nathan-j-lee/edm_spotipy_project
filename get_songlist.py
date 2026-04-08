import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


genre_cache = {}
artist_cache = {}


def fetch_and_cache(artist_name):
    """
    Checks the cache; if missing, calls Spotify once
    and stores both URL and Genres.
    """
    # Check if we already have this exact artist in memory
    if artist_name in artist_cache:
        return artist_cache[artist_name]

    try:
        results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        items = results['artists']['items']

        if not items:
            # Store None so we don't keep searching for a ghost
            artist_cache[artist_name] = None
            return None

        artist = items[0]
        # Store all useful data in one dictionary
        data = {
            "url": artist['external_urls']['spotify'],
            "genres": artist.get('genres', [])[:2],
            "popularity": artist.get('popularity', 0)
        }
        
        artist_cache[artist_name] = data
        return data

    except Exception as e:
        print(f"Spotify API Error for {artist_name}: {e}")
        return None

def get_artist_genres(artist_name):
    """Uses the cache to return genres."""
    data = fetch_and_cache(artist_name)
    return data['genres'] if data else []

def get_artist_URL(artist_name):
    """Uses the cache to return the URL."""
    data = fetch_and_cache(artist_name)
    return data['url'] if data else -1

def get_artist_tracks(artist_url):
    """Fetches tracks using a URL (usually called via AJAX)."""
    if not artist_url or artist_url == -1:
        return []
    try:
        # Note: Added country='US' for better results
        top_tracks = sp.artist_top_tracks(artist_url, country='US')
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