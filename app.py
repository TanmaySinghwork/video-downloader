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
        # THIS IS THE MODIFIED COMMAND BLOCK
        # We are now adding '--force-ipv6' to try a different connection route.
        command = [
            'yt-dlp',
            '--force-ipv6',  # <-- NEW FLAG
            '--no-check-certificate',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            '--dump-json',
            '--no-playlist',
            url
        ]
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            timeout=90
        )
        
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
        
        response_data = {
            'title': video_info.get('title'),
            'thumbnail': video_info.get('thumbnail'),
            'formats': formats
        }
        return jsonify(response_data)

    except Exception as e:
        error_output = "No specific error output captured."
        if hasattr(e, 'stderr') and e.stderr:
            error_output = e.stderr.strip()
        return jsonify({'error': f"A technical error occurred. Details from server: [ {error_output} ]"}), 500

@app.route('/ping')
def ping():
    return "pong", 200

if __name__ == '__main__':
    app.run(debug=True)