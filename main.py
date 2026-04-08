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
        
        from get_songlist import get_artist_genres

        # Define a helper function to process a single artist
        def process_artist(name):
            genres = get_artist_genres(name)
            time.sleep(0.1)
            return {
                'name': name,
                'genres': genres
            }

        # Threading Logic: max_workers=5 means 5 requests happen at once
        with ThreadPoolExecutor(max_workers=5) as executor:
            # .map maintains the order of the list
            enriched_artists = list(executor.map(process_artist, raw_names))

        return render_template('index.html', artists=enriched_artists)
        
    return "List was empty"


# Lazy load artist names rather than load every popular song
@app.route('/get_songs/<artist_name>')
def get_songs(artist_name):
    # Wrap in a list because your function expects a list
    result_map = get_artist_list([artist_name])
    
    # Extract the tracks for this specific artist
    tracks = result_map.get(artist_name, [])
    
    # Return as JSON so the browser can read it without refreshing
    return jsonify({"artist": artist_name, "tracks": tracks})


from concurrent.futures import ThreadPoolExecutor

# ... (other routes) ...

@app.route('/scrape', methods=['POST'])
def scrape_from_url():
    url = request.form.get('lineup_url')
    if not url:
        return redirect(url_for('home'))
    
    # 1. Get the raw list of names from Gemini
    raw_names = extract_lineup_with_ai(url)
    
    from get_songlist import get_artist_genres

    # 2. Reuse our helper for enrichment
    def process_artist(name):
        genres = get_artist_genres(name)
        return {
            'name': name,
            'genres': genres
        }

    # 3. Use threading to fetch genres quickly
    # Keeping max_workers at 5 to avoid those EDC rate limits!
    with ThreadPoolExecutor(max_workers=5) as executor:
        enriched_artists = list(executor.map(process_artist, raw_names))

    return render_template('index.html', artists=enriched_artists, url=url)

if __name__ == '__main__':
    app.run(debug=True)