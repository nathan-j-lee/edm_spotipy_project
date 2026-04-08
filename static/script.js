// --- INITIALIZATION & UI HANDLERS ---
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('loading-overlay');
    const uploadForm = document.getElementById('upload-form');
    const scrapeForm = document.getElementById('scrape-form');

    // Show loading spinner on submission
    if (scrapeForm) scrapeForm.addEventListener('submit', () => overlay.style.display = 'flex');
    if (uploadForm) uploadForm.addEventListener('submit', () => overlay.style.display = 'flex');

    // Generate filter buttons if a lineup exists
    if (document.getElementById('lineup-container')) {
        generateGenreButtons();
    }
});

// --- CORE TRACK FETCHING (The "Broken" Part) ---
function fetchSongs(detailsElement, artistName) {
    const contentDiv = detailsElement.querySelector('.song-list');
    
    // Only fetch if opening and not already loaded
    if (detailsElement.open && contentDiv.getAttribute('data-loaded') !== 'true') {
        
        // encodeURIComponent is critical for names with spaces or accents
        fetch(`/get_songs/${encodeURIComponent(artistName)}`)
            .then(response => {
                if (!response.ok) throw new Error('Artist data fetch failed');
                return response.json();
            })
            .then(data => {
                if (!data.tracks || data.tracks.length === 0) {
                    contentDiv.innerHTML = "<ul><li>No tracks found.</li></ul>";
                } else {
                    let listHtml = "<ul>";
                    data.tracks.forEach(track => {
                        listHtml += `<li>${track}</li>`;
                    });
                    listHtml += "</ul>";
                    contentDiv.innerHTML = listHtml;
                }
                contentDiv.setAttribute('data-loaded', 'true');
            })
            .catch(err => {
                contentDiv.innerHTML = "<ul><li>Error connecting to Spotify.</li></ul>";
                console.error(err);
            });
    }
}

// --- FILTERING AND SORTING LOGIC ---
function generateGenreButtons() {
    const entries = document.querySelectorAll('.artist-entry');
    const genreSet = new Set();
    
    entries.forEach(entry => {
        const genres = entry.getAttribute('data-genres').split(',');
        genres.forEach(g => { 
            if(g && g.trim() !== "") genreSet.add(g.trim());
        });
    });

    const filterContainer = document.getElementById('genre-filters');
    
    Array.from(genreSet).sort().forEach(genre => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn';
        btn.innerText = genre;
        btn.onclick = function() { filterGenre(genre, this); };
        filterContainer.appendChild(btn);
    });
}

function filterGenre(genre, clickedBtn) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    clickedBtn.classList.add('active');

    const entries = document.querySelectorAll('.artist-entry');
    entries.forEach(entry => {
        const artistGenres = entry.getAttribute('data-genres').split(',');
        entry.style.display = (genre === 'all' || artistGenres.includes(genre)) ? 'block' : 'none';
    });
}

function sortArtists() {
    const container = document.getElementById('lineup-container');
    const entries = Array.from(container.querySelectorAll('.artist-entry'));
    const sortBy = document.getElementById('sort-select').value;

    entries.sort((a, b) => {
        if (sortBy === 'name') return a.getAttribute('data-name').localeCompare(b.getAttribute('data-name'));
        if (sortBy === 'name-rev') return b.getAttribute('data-name').localeCompare(a.getAttribute('data-name'));
        if (sortBy === 'popularity') {
            return parseInt(b.getAttribute('data-popularity')) - parseInt(a.getAttribute('data-popularity'));
        }
    });

    entries.forEach(entry => container.appendChild(entry));
}

// --- MODAL TOGGLES ---
function toggleFilterMenu() {
    const menu = document.getElementById('filter-menu');
    menu.classList.toggle('show');
}

window.onclick = function(event) {
    const menu = document.getElementById('filter-menu');
    if (event.target == menu) {
        menu.classList.remove('show');
    }
}