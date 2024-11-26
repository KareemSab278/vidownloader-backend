from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from yt_dlp import YoutubeDL
import requests
import os
import logging

# Set up Flask app
app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "https://vidownloader-net.onrender.com"}})

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

@app.route('/download', methods=['POST'])
def download():
    # Get the request data
    data = request.get_json()
    url = data.get('url')
    
    # Log the incoming request
    logging.debug(f"Received URL: {url}")

    if not url:
        logging.error("No URL provided.")
        return jsonify({'error': 'No URL provided'}), 400

    # yt-dlp options
    ydl_opts = {
        'format': 'mp4',
        'quiet': False,  # Enable logging
        'cookiefile': 'cookies.txt',  # Required for Instagram
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': url,
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        },
        'nocheckcertificate': True,  # Avoid SSL issues
        'outtmpl': '-',  # Stream content directly
    }

    try:
        # Use yt-dlp to fetch or download the video
        logging.debug("Using yt-dlp to fetch video information...")
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            download_link = info_dict.get('url')
            logging.debug(f"Download link obtained: {download_link}")

            if not download_link:
                logging.error("No download link found.")
                return jsonify({'error': 'No download link found.'}), 500

        # Stream the video content to the user
        logging.debug("Fetching video content...")
        headers = ydl_opts['http_headers']
        video_response = requests.get(download_link, headers=headers, stream=True)
        logging.debug(f"Video response status code: {video_response.status_code}")

        if video_response.status_code == 200:
            logging.debug("Streaming video to the user...")
            return Response(
                video_response.iter_content(chunk_size=8192),
                content_type=video_response.headers['Content-Type'],
                headers={"Content-Disposition": f"attachment; filename={info_dict['title']}.mp4"},
            )

        logging.error("Failed to fetch video content.")
        return jsonify({'error': 'Failed to download video from the source.'}), 500

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'Failed to process the request.', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
