from flask import Flask, make_response, request, Response
import flask
import pathlib
#import librosa
#import tempfile


app = Flask(__name__, static_url_path='')
i = [0]

@app.route('/')
def root():
    return app.send_static_file('m.html')


@app.route('/a', methods=['POST'])
def a():
    blob = request.data

    print("Received:", blob)
    with open(f'outo.opus', 'wb') as of:
        of.write(blob)

    # tp = tempfile.NamedTemporaryFile(delete=False, suffix='.opus')
    # tp.write(blob)
    # tp.close()
    #
    # l = librosa.load(tp.name, sr=16000)

    return {'test': f'{i}'}

@app.route('/test2.js')
def test2():
   response = flask.make_response(flask.send_file(pathlib.Path('static/processors.js')))
   response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
   return response

if __name__ == '__main__':
    app.run()