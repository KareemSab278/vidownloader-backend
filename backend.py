from flask import Flask, request, jsonify
from flask_cors import CORS
from yt_dlp import YoutubeDL

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://vidownloader-net.onrender.com"}})  # Adjust origin as needed

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'format': 'mp4',
        'quiet': True,
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
    app.run(host='0.0.0.0', port=3000)
