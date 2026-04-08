import time

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor

from get_songlist import get_artist_list
from ai_utils import extract_lineup_with_ai

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'text_files'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_artists_from_file():
    # Adjust path if your text file name/location is different
    file_path = os.path.join('text_files', 'Proper_Countdown_Day1.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            # Read lines and strip whitespace/newlines
            return [line.strip() for line in f if line.strip()]
    return []


@app.route('/')
def home():
    return render_template('index.html')



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        raw_names = []
        with open(filepath, 'r') as f:
            content = f.read()
            # Clean up names from file
            raw_names = [name.strip() for name in content.replace('\n', ',').split(',') if name.strip()]
        
        from get_songlist import fetch_and_cache

        # Define a helper function to process a single artist
        def process_artist(name):
            data = fetch_and_cache(name)
            time.sleep(0.1)
            return {
                'name': name,
                'genres': data['genres'] if data else [],
                'popularity': data['popularity'] if data else 0
            }

        # Threading Logic: max_workers=5 means 5 requests happen at once
        with ThreadPoolExecutor(max_workers=5) as executor:
            # .map maintains the order of the list
            enriched_artists = list(executor.map(process_artist, raw_names))

        return render_template('index.html', artists=enriched_artists)
        
    return "List was empty"


@app.route('/get_songs/<artist_name>')
def get_songs(artist_name):
    # Import the new cached functions
    from get_songlist import get_artist_URL, get_artist_tracks

    print(f"Fetching tracks for: {artist_name}") # Debugging line
    
    # 1. This now checks your 'artist_cache' dictionary first.
    # Since you just uploaded the file, the URL is already in memory!
    artist_url = get_artist_URL(artist_name)
    
    # 2. Only fetch the tracks if we have a valid URL
    if artist_url != -1:
        tracks = get_artist_tracks(artist_url)
    else:
        tracks = []
    
    # Return as JSON for script.js to pick up
    return jsonify({"artist": artist_name, "tracks": tracks})


from concurrent.futures import ThreadPoolExecutor

# ... (other routes) ...

@app.route('/scrape', methods=['POST'])
def scrape_from_url():
    url = request.form.get('lineup_url')
    if not url:
        return redirect(url_for('home'))
    
    # 1. This is where raw_names is born (from your AI utility)
    raw_names = extract_lineup_with_ai(url)
    
    from get_songlist import fetch_and_cache

    # 2. Define the helper to fill the cache and get genres/popularity
    def process_artist(name):
        data = fetch_and_cache(name)
        return {
            'name': name,
            'genres': data['genres'] if data else [],
            'popularity': data['popularity'] if data else 0
        }

    # 3. Use Threading just like the upload route
    with ThreadPoolExecutor(max_workers=5) as executor:
        enriched_artists = list(executor.map(process_artist, raw_names))

    # 4. Pass 'url' back so it stays in the input field if needed
    return render_template('index.html', artists=enriched_artists, url=url)

if __name__ == '__main__':
    app.run(debug=True)