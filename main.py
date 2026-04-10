from flask import Flask, jsonify, request
import yt_dlp
import re

app = Flask(__name__)

def is_valid_video_id(vid):
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', vid))

@app.route('/audio')
def get_audio():
    video_id = request.args.get('id', '').strip()
    if not video_id or not is_valid_video_id(video_id):
        return jsonify({'error': 'ID inválido'}), 400

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f'https://www.youtube.com/watch?v={video_id}',
                download=False
            )
            # Buscar el mejor formato de solo audio
            audio_url = None
            duration  = int(info.get('duration', 0))
            title     = info.get('title', '')
            thumbnail = info.get('thumbnail', '')

            for fmt in (info.get('formats') or []):
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    audio_url = fmt.get('url')
                    break

            # Si no hay formato solo-audio, usar el mejor disponible
            if not audio_url:
                audio_url = info.get('url') or info.get('webpage_url')

            if not audio_url:
                return jsonify({'error': 'No se pudo obtener URL de audio'}), 404

            return jsonify({
                'url':       audio_url,
                'duration':  duration,
                'title':     title,
                'thumbnail': thumbnail
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []})

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch10',
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'ytsearch10:{query}', download=False)
            results = []
            for entry in (info.get('entries') or []):
                results.append({
                    'id':        entry.get('id', ''),
                    'title':     entry.get('title', ''),
                    'duration':  int(entry.get('duration') or 0),
                    'thumbnail': entry.get('thumbnail', ''),
                    'channel':   entry.get('channel', entry.get('uploader', '')),
                })
            return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e), 'results': []}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
