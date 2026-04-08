        const overlay = document.getElementById('loading-overlay');
        const uploadForm = document.getElementById('upload-form');
        const scrapeForm = document.getElementById('scrape-form');

        // ADDED: Listener for the Scrape form
        scrapeForm.addEventListener('submit', function () {
            overlay.style.display = 'block';
        });

        uploadForm.addEventListener('submit', function () {
            overlay.style.display = 'block';
        });

        function fetchSongs(detailsElement, artistName) {
            const contentDiv = detailsElement.querySelector('.song-list');
            if (detailsElement.open && contentDiv.getAttribute('data-loaded') !== 'true') {

                fetch(`/get_songs/${encodeURIComponent(artistName)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.tracks === -1 || data.tracks.length === 0) {
                            contentDiv.innerHTML = "<em>No tracks found.</em>";
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
                        contentDiv.innerHTML = "Error loading songs.";
                        console.error(err);
                    });
            }
        }