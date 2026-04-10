from flask import Flask, jsonify, request
import yt_dlp
import re

app = Flask(__name__)

def is_valid_video_id(vid):
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', vid))

def try_extract(video_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5_1 like Mac OS X)',
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
        audio_url = None
        for fmt in sorted(info.get('formats') or [], key=lambda f: f.get('abr') or 0, reverse=True):
            if fmt.get('acodec') not in (None, 'none') and fmt.get('vcodec') in (None, 'none'):
                url = fmt.get('url', '')
                if url.startswith('http'):
                    audio_url = url
                    break
        if not audio_url:
            audio_url = info.get('url', '')
        return audio_url, int(info.get('duration', 0)), info.get('title', ''), info.get('thumbnail', '')

@app.route('/audio')
def get_audio():
    video_id = request.args.get('id', '').strip()
    if not video_id or not is_valid_video_id(video_id):
        return jsonify({'error': 'ID inválido'}), 400
    try:
        audio_url, duration, title, thumbnail = try_extract(video_id)
        if audio_url and audio_url.startswith('http'):
            return jsonify({'url': audio_url, 'duration': duration, 'title': title, 'thumbnail': thumbnail})
        return jsonify({'error': 'Sin URL de audio'}), 500
    except Exception as e:
        return jsonify({'error': str(e)[:200]}), 500

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []})
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'ytsearch10:{query}', download=False)
            results = []
            for entry in (info.get('entries') or []):
                vid_id = entry.get('id', '')
                if not vid_id:
                    continue
                results.append({
                    'id':        vid_id,
                    'title':     entry.get('title', ''),
                    'duration':  int(entry.get('duration') or 0),
                    'thumbnail': entry.get('thumbnail', f'https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg'),
                    'channel':   entry.get('channel', entry.get('uploader', '')),
                })
            return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e), 'results': []}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
