import eventlet
import socketio

import numpy as np

from online_wrapper import OnlineCodeTranscriber


sio = socketio.Server()
app = socketio.WSGIApp(
    sio,
    static_files={
        "/": {"content_type": "text/html", "filename": "./public/index.html"},
        "": "./public",
    },
)

transcriber = OnlineCodeTranscriber()


@sio.event
def connect(sid, environ):
    print(f"connect {sid}")


@sio.event
def audio_in(sid, data):
    signal = np.frombuffer(data, dtype=np.int16)
    text = transcriber.transcribe(signal)
    sio.emit("transcript", {"transcript": text, "i": int(signal[0])})


@sio.event
def disconnect(sid):
    print(f"disconnect {sid}")


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(("", 3000)), app)
