from flask import Flask, request, jsonify, send_file
from io import BytesIO
import os
import pytube
from pytube.exceptions import RegexMatchError
from flask_cors import CORS

from api.helpers import download_stream_via_buffer

app = Flask(__name__)
cors = CORS(app, origins=['http://localhost:3000', 'https://ytsave.vercel.app'])


@app.route('/save_hd', methods=['GET'])
def save_video_hd():
    print("Request params:", request.args)

    video_url = request.args.get('url')
    format_type = request.args.get('format')

    if not video_url or not format_type or format_type not in ['video', 'audio']:
        return jsonify({'error': 'Bad request: missing `video` and/or `format` inputs.'}), 400

    try:
        youtube = pytube.YouTube(video_url)
        stream = youtube.streams.get_highest_resolution() if format_type == 'video' \
            else youtube.streams.get_audio_only()

        return download_stream_via_buffer(stream, youtube.title)
    except RegexMatchError:
        return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save', methods=['GET'])
def save_video_by_itag():
    print("Request params:", request.args)

    video_url = request.args.get('url')
    itag = int(request.args.get('itag'))

    print(video_url, itag)
    if not video_url or not itag:
        return jsonify({'error': 'Bad request, missing `video` and/or `itag` inputs.'}), 400

    try:
        youtube = pytube.YouTube(video_url)
        stream = youtube.streams.get_by_itag(itag)
        if stream is None:
            return jsonify({'error': 'Video not found, invalid url or itag'}), 404

        return download_stream_via_buffer(stream, youtube.title)

    except RegexMatchError:
        return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/info', methods=['GET'])
def get_video_metadata():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({'error': 'Bad request: missing video URL'}), 400

    try:
        youtube = pytube.YouTube(video_url)

        video_metadata = {
            'title': youtube.title,
            'author': youtube.author,
            'length': youtube.length,
            'views': youtube.views,
            'rating': youtube.rating,
            'thumbnail_url': youtube.thumbnail_url,
        }

        # Get all available streams
        video_streams = youtube.streams.filter(file_extension='mp4').order_by('resolution').desc()
        audio_streams = youtube.streams.filter(only_audio=True, file_extension='mp4')
        streams = [*video_streams, *audio_streams]

        # TODO: filter list further -> one option per resolution (prefer non progressive over progressive)
        stream_options = []
        for stream in streams:
            stream_info = {
                'resolution': stream.resolution,
                'mime_type': stream.mime_type,
                'abr': stream.abr,
                'video_codec': stream.video_codec,
                'audio_codec': stream.audio_codec,
                'is_progressive': stream.is_progressive,
                'itag': stream.itag,
                'type': stream.type
            }
            stream_options.append(stream_info)

        video_metadata['streams'] = stream_options
        return jsonify(video_metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Service up and running.'}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
