FROM python:3.7

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y libsndfile1 ffmpeg
RUN pip install Cython
RUN pip install nemo_toolkit[all]

EXPOSE 5000

COPY . .

ENV FLASK_APP server.py
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]
