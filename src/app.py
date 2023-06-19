from flask import Flask, request, send_file, jsonify
import pytube
from pytube.exceptions import RegexMatchError

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
        # Create a YouTube object
        youtube = pytube.YouTube(video_url)
        stream = youtube.streams.get_highest_resolution() if format_type == 'video' \
            else youtube.streams.get_audio_only()
        file_path = stream.download()
        return send_file(file_path, as_attachment=True)
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
    app.run()
