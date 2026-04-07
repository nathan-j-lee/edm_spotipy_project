import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from tkinter_test import prompt_user

# This looks for a .env file in the same directory and loads it
load_dotenv()

# This automatically looks for the environment variables we set
scope = "user-library-read"

# authenticate Spotify based on the scope above
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# Test it
results = sp.current_user_saved_tracks(limit=1)
#print("Successfully connected to Spotify!")

# Search for an artist's name and return their external URL
def get_artist_URL(artist_name):

    # Use search query to find artist based on artist_name parameter
    results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)

    # results is a large JSON object, is in 'artists' -> 'items'
    results_items = results['artists']['items']

    # if not found, return -1, else return the URL from the found JSON
    if len(results_items) < 1:
        print("ERROR: Artist name search not found")
        return -1
    else:
        artist = results_items[0]
        return artist['external_urls']['spotify']
    
# Use previous example of artist_top_tracks() method, but with using the get_artist_URL() method
def get_artist_tracks(artist_URL):
    # If the artist search did not work, stop the function
    if (artist_URL == -1):
        print("ERROR: Artist URL not found")
        return -1
    top_tracks = sp.artist_top_tracks(artist_URL, country='US')

    track_names = [track['name'] for track in top_tracks['tracks']]
    #track_pop = [track['popularity'] for track in top_tracks['tracks']]

    #for track, pop in zip(track_names, track_pop):
    #    print(f"name: {track} - popularity: {pop}")

    return track_names
# want to input a list of names, which should run above for each of the names and output a list of tracks per artist

def get_artist_list(list):
    print("Searching for artists on Spotify...")
    #user_input = "Above & Beyond, AK SPORTS, AR/CO, Cera Khin, Clara Cuvé, Close Friends Only, Crankdat, CRAY, Discovery Project, GRAVAGERZ, Harristone, Hedex, John Summit, Kaysin, Kevin de Vries, Kobosil, Lucati, Madeon , Marie Nyx, MPH, Odymel, Pryda, Reza, Ship Wrek, Shlømo, SLANDER, southstar, Starjunk 95, Sub Focus, Techno Tupac, Wuki"

    artist_map = {}

    #print(parsed_input)
    # grab top tracks

    for artist in list:
        print(f"Looking for {artist}")
        artist_tracks = get_artist_tracks(get_artist_URL(artist))

        artist_map[artist] = artist_tracks

    return artist_map

def read_files():
    print("Reading files...")
    # grab file from prompted user
    filepath = "text_files\Proper_Countdown_Day1.txt"

    with open(filepath, 'r') as file:
        # .read() gets the whole string, .splitlines() turns it into a list
        artist_list = file.read().splitlines()

    # Clean up any potential empty lines or extra spaces
    artist_list = [name.strip() for name in artist_list if name.strip()]

    return artist_list

#lineup_list = read_files()
#test = get_artist_list(lineup_list)
#print(test)

#for artist, tracks in test.items():
#    print(f'Artist: {artist}')
#    if tracks == -1:
#        print(" Not found!")
#    else:
#        for track in tracks:
#            print(f' - {track}')

