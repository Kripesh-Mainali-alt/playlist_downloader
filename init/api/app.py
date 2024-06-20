from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Playlist Downloader</title>
    </head>
    <body>
        <h1>YouTube Playlist Downloader</h1>
        <form id="playlistForm">
            <label for="playlistUrl">Enter YouTube Playlist URL:</label>
            <input type="text" id="playlistUrl" name="playlistUrl">
            <button type="button" onclick="fetchPlaylist()">Get Links</button>
        </form>
        <div id="links">
            <textarea id="downloadLinks" rows="10" cols="100"></textarea>
        </div>
        <script>
            async function fetchPlaylist() {
                const playlistUrl = document.getElementById('playlistUrl').value;
                const response = await fetch('/get_links', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: playlistUrl }),
                });
                const links = await response.json();
                const linksTextarea = document.getElementById('downloadLinks');
                linksTextarea.value = '';
                if (response.ok) {
                    links.forEach((link, index) => {
                        linksTextarea.value += `${link.url}\n`;
                    });
                } else {
                    linksTextarea.value = links.error;
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/get_links', methods=['POST'])
def get_links():
    data = request.json
    playlist_url = data.get('url')
    video_infos = extract_video_infos(playlist_url)
    if not video_infos:
        return jsonify({"error": "Invalid YouTube playlist URL or no videos found"}), 400

    download_links = []
    for index, video_info in enumerate(video_infos):
        direct_url = generate_direct_link(video_info['url'])
        filename = f"{index + 1}. {sanitize_filename(video_info['title'])}.mp4"
        download_links.append({
            'url': f'{direct_url}&title={filename}',
            'title': video_info['title'],
            'filename': filename
        })

    return jsonify(download_links)

def extract_video_infos(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        if 'entries' in result:
            return [{'url': entry['url'], 'title': entry['title']} for entry in result['entries']]
    return []

def generate_direct_link(video_url):
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        return info_dict.get('url')

def sanitize_filename(filename):
    return "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename)

if __name__ == '__main__':
    app.run(debug=True)
