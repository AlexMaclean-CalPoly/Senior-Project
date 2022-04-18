import time

import numpy as np
import pyaudio as pa
from torch.utils.data import DataLoader

import beam
import online


def main():
    SAMPLE_RATE = 16000  # sample rate, Hz
    FRAME_LEN = 1.0    # duration of signal frame, seconds
    CHANNELS = 1    # number of audio channels (expect mono signal)
    CHUNK_SIZE = int(FRAME_LEN * SAMPLE_RATE)

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

    p = pa.PyAudio()
    input_devices = get_input_devices(p)

    if not len(input_devices):
        print('ERROR: No audio input device found.')
        exit(1)

    dev_idx = -2
    while dev_idx not in input_devices:
        print('Please type input device ID:')
        dev_idx = int(input())

    def callback(in_data, frame_count, time_info, status):
        signal = np.frombuffer(in_data, dtype=np.int16)
        # print(in_data)
        logits = asr.transcribe(signal)
        text = beam_search.process(softmax(logits))
        print(text)
        return in_data, pa.paContinue


    stream = p.open(format=pa.paInt16,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    input_device_index=dev_idx,
                    stream_callback=callback,
                    frames_per_buffer=CHUNK_SIZE)

    print('Listening...')

    stream.start_stream()

    # Interrupt kernel and then speak for a few more words to exit the pyaudio loop !
    try:
        while stream.is_active():
            time.sleep(0.1)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

        print()
        print("PyAudio stopped")


def get_input_devices(p):
    print('Available audio input devices:')
    input_devices = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev.get('maxInputChannels'):
            input_devices.append(i)
            print(i, dev.get('name'))

    return input_devices


def softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum(axis=-1).reshape([logits.shape[0], 1])


if __name__ == '__main__':
    main()