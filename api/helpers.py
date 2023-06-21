from io import BytesIO
from flask import send_file


def download_stream_via_buffer(stream, title):
    buffer = BytesIO()
    stream.stream_to_buffer(buffer)
    buffer.seek(0)

    filename = f'{title}.mp4' if stream.type == 'video' \
        else f'{title}.mp3'
    file = send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="video/mp4")
    return file
