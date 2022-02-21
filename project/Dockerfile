FROM python:3.7

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y libsndfile1 ffmpeg build-essential cmake

RUN python -m pip install --upgrade pip
RUN pip install Cython
RUN pip install torch==1.8.1 torchvision==0.9.1 torchaudio==0.8.1
RUN pip install git+https://github.com/NVIDIA/NeMo.git@r1.6.2#egg=nemo_toolkit[all]

RUN apt-get install -y swig
RUN git clone https://github.com/NVIDIA/NeMo -b r1.6.2
RUN cd NeMo && bash scripts/asr_language_modeling/ngram_lm/install_beamsearch_decoders.sh

COPY . .

RUN python build_setup.py

CMD [ "python", "./baseline.py", "test-audio-2.wav" ]