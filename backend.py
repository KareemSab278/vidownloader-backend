from flask import Flask, request, jsonify
from flask_cors import CORS
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "https://vidownloader-net.onrender.com"}})

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'format': 'mp4',
        'quiet': False,  # Verbose logging for debugging
        'proxy': 'http://44.195.247.145:80',  # The selected proxy
        'cookiefile': 'cookies.txt',  # Ensure this file contains valid TikTok cookies
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            download_link = info_dict.get('url')

            if not download_link:
                return jsonify({'error': 'No download link found.'}), 500

            return jsonify({'downloadLink': download_link})

    except Exception as e:
        return jsonify({'error': 'Failed to fetch download link.', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
