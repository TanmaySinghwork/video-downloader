import json
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_video_info', methods=['POST'])
def get_video_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        command = ['yt-dlp', '--dump-json', '--no-playlist', url]
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=90)
        video_info = json.loads(result.stdout)
        formats = []
        for f in video_info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                formats.append({
                    'format_note': f.get('format_note', 'N/A'),
                    'ext': f.get('ext'),
                    'filesize_approx': f.get('filesize_approx', 0),
                    'url': f.get('url')
                })
        response_data = {'title': video_info.get('title'), 'thumbnail': video_info.get('thumbnail'), 'formats': formats}
        return jsonify(response_data)
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'The request timed out. The video might be too long or the server is busy.'}), 500
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to fetch video information. The URL might be invalid or the video is protected.'}), 500
    except Exception as e:
        return jsonify({'error': 'An unknown error occurred. Please try again.'}), 500

@app.route('/ping')
def ping():
    return "pong", 200                                                    