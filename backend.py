import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from yt_dlp import YoutubeDL
import logging

app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "*"}})

logging.basicConfig(level=logging.DEBUG)

# Path to the cookies file
DEFAULT_COOKIES_PATH = "cookies.txt"
BROWSER_COOKIES_PATH = "/opt/render/.config/microsoft-edge"

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    logging.debug(f"Received URL: {url}")

    if not url:
        logging.error("No URL provided.")
        return jsonify({'error': 'No URL provided'}), 400

    # Use browser-extracted cookies if available, fallback to cookies.txt
    cookies_path = BROWSER_COOKIES_PATH if os.path.exists(BROWSER_COOKIES_PATH) else DEFAULT_COOKIES_PATH
    logging.info(f"Using cookies file: {cookies_path}")

    # yt-dlp options
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'cookiefile': cookies_path,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
        'verbose': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            logging.debug("Starting yt-dlp extraction...")
            info_dict = ydl.extract_info(url, download=False)
            logging.debug(f"Extracted info_dict: {info_dict}")

            # Get download link
            download_link = info_dict.get('url') or (
                info_dict['formats'][-1]['url'] if 'formats' in info_dict else None
            )
            logging.debug(f"Download link: {download_link}")

            if not download_link:
                logging.error("No download link found.")
                return jsonify({'error': 'No download link found.'}), 500

        # Fetch the video content
        headers = ydl_opts['http_headers']
        video_response = requests.get(download_link, headers=headers, stream=True)
        logging.debug(f"Video response status code: {video_response.status_code}")

        if video_response.status_code == 200:
            return Response(
                video_response.iter_content(chunk_size=8192),
                content_type=video_response.headers.get('Content-Type', 'application/octet-stream'),
                headers={"Content-Disposition": f"attachment; filename=\"{info_dict['title']}.mp4\""},
            )

        logging.error(f"Failed to fetch video content: {video_response.status_code}")
        return jsonify({'error': 'Failed to fetch video content.', 'status': video_response.status_code}), 500

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'Failed to process the request.', 'details': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

#     port = int(os.environ.get("PORT", 3000))
#     app.run(host='0.0.0.0', port=port)

# yt-dlp options
