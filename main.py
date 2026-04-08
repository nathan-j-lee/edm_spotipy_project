from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename


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
        
        # Parse the file immediately after saving
        artists = []
        with open(filepath, 'r') as f:
            content = f.read()
            # Replace newlines with commas so we can split everything at once
            # This handles: "Artist A, Artist B" AND "Artist A\nArtist B"
            raw_list = content.replace('\n', ',').split(',')
            # Clean up whitespace and ignore empty entries
            artists = [name.strip() for name in raw_list if name.strip()]
        return render_template('index.html', artists=artists)
    return "List was empty"

"""
        # Start sending artists to Spotipy
        if artists:
            # Simple: Take first artist from list
            #test_artist = artists[:1]

            artist_map = get_artist_list(artists)

            return render_template('index.html',
                                   artist_map = artist_map,
                                   filename = filename)
"""
    
    


# Lazy load artist names rather than load every popular song
@app.route('/get_songs/<artist_name>')
def get_songs(artist_name):
    # Wrap in a list because your function expects a list
    result_map = get_artist_list([artist_name])
    
    # Extract the tracks for this specific artist
    tracks = result_map.get(artist_name, [])
    
    # Return as JSON so the browser can read it without refreshing
    return jsonify({"artist": artist_name, "tracks": tracks})


# Use Gemini to scrape lineup from given URL
@app.route('/scrape', methods=['POST'])
def scrape_from_url():
    url = request.form.get('lineup_url')
    if not url:
        return redirect(url_for('home'))
    
    artists = extract_lineup_with_ai(url)

    return render_template('index.html', artists=artists, url=url)

if __name__ == '__main__':
    app.run(debug=True)