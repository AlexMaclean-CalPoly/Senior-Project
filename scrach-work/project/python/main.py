import numpy as np

from online_wrapper import OnlineCodeTranscriber
import sys

SAMPLE_RATE = 16000  # sample rate, Hz
FRAME_LEN = 1.0    # duration of signal frame, seconds
CHUNK_SIZE = int(FRAME_LEN * SAMPLE_RATE)
INT_SIZE = 2 # bytes

def main():
    transcriber = OnlineCodeTranscriber()

    while True:
        in_data = sys.stdin.buffer.read(CHUNK_SIZE * INT_SIZE)
        signal = np.frombuffer(in_data, dtype=np.int16)
        text = transcriber.transcribe(signal)
        print(f'{signal[0]} {text}')
        sys.stdout.flush()


if __name__ == '__main__':
    main()