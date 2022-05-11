import numpy as np

# from nemo.utils.nemo_logging import Logger

# nemo_logger = Logger()
# nemo_logger.remove_stream_handlers()
# nemo_logger.add_file_handler('log.txt')

from torch.utils.data import DataLoader

from beam_search import BeamSearch
from frame_asr import FrameASR, AudioDataLayer, get_asr_model
from racket_normalize import racket_inverse_normalizer

import sys

SAMPLE_RATE = 16000  # sample rate, Hz


class OnlineCodeTranscriber:
    def __init__(self):
        cfg, asr_model = get_asr_model()
        data_layer = AudioDataLayer(sample_rate=cfg.preprocessor.sample_rate)
        data_loader = DataLoader(
            data_layer, batch_size=1, collate_fn=data_layer.collate_fn
        )

        self.asr = FrameASR(
            model_definition={
                "sample_rate": SAMPLE_RATE,
                "AudioToMelSpectrogramPreprocessor": cfg.preprocessor,
                "JasperEncoder": cfg.encoder,
                "labels": cfg.decoder.vocabulary,
            },
            asr_model=asr_model,
            data_loader=data_loader,
            data_layer=data_layer,
            frame_overlap=1,
        )

        self.beam_search = BeamSearch(lambda x: 1, list(cfg.decoder.vocabulary))
        self.search_state = BeamSearch.start_state()

        self.normalizer = racket_inverse_normalizer()

        sys.stdout.buffer.write(b"[Ready]\r\n")
        sys.stdout.flush()

    def transcribe(self, signal):
        logits, draft_logits = self.asr.transcribe(signal)
        self.search_state = self.beam_search(
            self.softmax(logits), self.search_state, space=True
        )
        draft_state = self.beam_search(self.softmax(draft_logits), self.search_state)
        text = draft_state.A[0]
        # return text
        return self.normalizer.inverse_normalize(text)

    @staticmethod
    def softmax(logits):
        e = np.exp(logits - np.max(logits))
        return e / e.sum(axis=-1).reshape([logits.shape[0], 1])
