FROM python:3.7-buster

RUN apt-get update
RUN apt-get install --yes libsndfile1 ffmpeg
RUN pip install Cython nemo_toolkit[all]
RUN pip install eventlet python-socketio

WORKDIR /usr/src/app

COPY ./src/racket_tagger ./racket_tagger
RUN python racket_tagger/tagger.py && rm -rf racket_tagger

COPY ./src/ .

EXPOSE 3000

ENTRYPOINT ["python", "server.py"]