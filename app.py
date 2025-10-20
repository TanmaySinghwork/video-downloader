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
        # Command to get video info as JSON, timeout after 90 seconds
        command = ['yt-dlp', '--dump-json', '--no-playlist', url]
        
        # Execute the command. The 'check=True' will cause an error to be raised if yt-dlp fails.
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

    # This is the new, detailed error-catching block
    except Exception as e:
        # Default error message
        error_output = "No specific error output captured."
        
        # Check if the exception 'e' has the 'stderr' attribute, which contains the actual error from yt-dlp
        if hasattr(e, 'stderr') and e.stderr:
            error_output = e.stderr.strip()

        # Return a JSON response with the detailed error for debugging
        return jsonify({'error': f"A technical error occurred. Details from server: [ {error_output} ]"}), 500

# This special route is for our Uptime Pinger
@app.route('/ping')
def ping():
    return "pong", 200

# This part is for running on your own PC, Render will use a different command
if __name__ == '__main__':
    app.run(debug=True)