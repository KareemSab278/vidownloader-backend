from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from yt_dlp import YoutubeDL
import requests
import os
import logging
import yt_dlp.utils

# Set up Flask app
app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "https://vidownloader-net.onrender.com"}})

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Check for cookies file
if not os.path.exists('cookies.txt'):
    logging.error("The cookies.txt file is missing! Make sure it exists and is correctly formatted.")

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    logging.debug(f"Received URL: {url}")

    if not url:
        logging.error("No URL provided.")
        return jsonify({'error': 'No URL provided'}), 400

    # yt-dlp options
    ydl_opts = {
        'format': 'mp4',
        'cookiefile': 'cookies.txt',  # Ensure this file exists and is updated
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        },
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            logging.debug("Starting yt-dlp extraction...")
            info_dict = ydl.extract_info(url, download=False)
            download_link = info_dict.get('url')
            logging.debug(f"Download link: {download_link}")

            if not download_link:
                logging.error("No download link found.")
                return jsonify({'error': 'No download link found.'}), 500

        # Fetch video content
        headers = ydl_opts['http_headers']
        video_response = requests.get(download_link, headers=headers, stream=True)
        logging.debug(f"Video response status code: {video_response.status_code}")

        if video_response.status_code == 200:
            logging.debug("Streaming video to the user...")
            return Response(
                video_response.iter_content(chunk_size=8192),
                content_type=video_response.headers.get('Content-Type', 'application/octet-stream'),
                headers={"Content-Disposition": f"attachment; filename={info_dict['title']}.mp4"},
            )

        logging.error(f"Failed to fetch video content. Status: {video_response.status_code}")
        return jsonify({'error': 'Failed to fetch video content.', 'status': video_response.status_code}), 500

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"yt-dlp DownloadError: {str(e)}")
        return jsonify({'error': 'The provided URL is not supported.', 'details': str(e)}), 400

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({'error': 'Failed to process the request.', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
