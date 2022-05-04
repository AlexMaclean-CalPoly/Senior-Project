# import time

import numpy as np
import pyaudio as pa
from torch.utils.data import DataLoader

import beam
import online
import sys
import time


SAMPLE_RATE = 16000  # sample rate, Hz
FRAME_LEN = 1.0    # duration of signal frame, seconds
CHANNELS = 1    # number of audio channels (expect mono signal)
CHUNK_SIZE = int(FRAME_LEN * SAMPLE_RATE)
INT_SIZE = 2 # bytes

def main():
    cfg, asr_model = online.get_asr_model()
    data_layer = online.AudioDataLayer(sample_rate=cfg.preprocessor.sample_rate)
    data_loader = DataLoader(data_layer, batch_size=1, collate_fn=data_layer.collate_fn)
    beam_search = beam.BeamSearch(lambda x: 1, list(cfg.decoder.vocabulary))

    asr = online.FrameASR(
        model_definition={
            'sample_rate': SAMPLE_RATE,
            'AudioToMelSpectrogramPreprocessor': cfg.preprocessor,
            'JasperEncoder': cfg.encoder,
            'labels': cfg.decoder.vocabulary
        },
        asr_model=asr_model,
        data_loader=data_loader,
        data_layer=data_layer,
        frame_len=FRAME_LEN,
        frame_overlap=2,
        offset=4)

    sys.stdout.buffer.write(b'[Ready]\r\n')
    sys.stdout.flush()

    while True:
        in_data = sys.stdin.buffer.read(CHUNK_SIZE * INT_SIZE)
        signal = np.frombuffer(in_data, dtype=np.int16)

        logits = asr.transcribe(signal)
        text = beam_search.process(softmax(logits))
        print(text)
        sys.stdout.flush()


def softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum(axis=-1).reshape([logits.shape[0], 1])


if __name__ == '__main__':
    main()