from flask import Flask, request, jsonify, send_file
from io import BytesIO
import pytube
from pytube.exceptions import RegexMatchError
import os

app = Flask(__name__)


@app.route("/")
def helloworld():
    return "Hello there, to save a video try this endpoint: /save?url=<VIDEO_URL>&format=<[audio, video]>"


# /save?video-url=<VIDEO_URL>&format=<FORMAT>
@app.route('/save', methods=['GET'])
def save_video():
    print("Request params:", request.args)

    video_url = request.args.get('url')
    format_type = request.args.get('format')

    if not video_url or not format_type or format_type not in ['video', 'audio']:
        return 'Invalid request parameters', 400

    try:
        youtube = pytube.YouTube(video_url)
        stream = youtube.streams.get_highest_resolution() if format_type == 'video' \
            else youtube.streams.get_audio_only()

        # Download to a buffer
        buffer = BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)

        filename = f'{youtube.title}.mp4' if format_type == 'video'\
            else f'{youtube.title}.mp3'

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="video/mp4",
        )
    except RegexMatchError:
        return 'Video not found', 404
    except Exception as e:
        return str(e), 500


@app.route('/info', methods=['GET'])
def get_video_metadata():
    video_url = request.args.get('url')

    if not video_url:
        return 'Missing video URL', 400

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
        streams = youtube.streams
        stream_options = []
        for stream in streams:
            stream_info = {
                'resolution': stream.resolution,
                'mime_type': stream.mime_type,
                'abr': stream.abr,
                'video_codec': stream.video_codec,
                'audio_codec': stream.audio_codec,
                'is_progressive': stream.is_progressive,
            }
            stream_options.append(stream_info)

        video_metadata['streams'] = stream_options
        return jsonify(video_metadata)
    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)