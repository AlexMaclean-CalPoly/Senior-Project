import copy

import nemo.collections.asr as nemo_asr
import numpy as np
import torch
from nemo.core.classes import IterableDataset
from nemo.core.neural_types import NeuralType, AudioSignal, LengthsType
from omegaconf import OmegaConf
import json
from pathlib import Path


def get_new_config(cfg):
    OmegaConf.set_struct(cfg.preprocessor, False)

    with open(Path(__file__).parent / 'normalization.json', 'r') as in_file:
        normalization = json.load(in_file)

    cfg.preprocessor.normalize = normalization
    cfg.preprocessor.dither = 0.0
    cfg.preprocessor.pad_to = 0

    OmegaConf.set_struct(cfg.preprocessor, True)

    return cfg


def get_asr_model():
    asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained('QuartzNet15x5Base-En')
    cfg = get_new_config(copy.deepcopy(asr_model._cfg))
    asr_model.preprocessor = asr_model.from_config_dict(cfg.preprocessor)

    # Set model to inference mode
    asr_model.eval()
    asr_model = asr_model.to(asr_model.device)
    return cfg, asr_model


class AudioDataLayer(IterableDataset):

    @property
    def output_types(self):
        return {
            'audio_signal': NeuralType(('B', 'T'), AudioSignal(freq=self._sample_rate)),
            'a_sig_length': NeuralType(tuple('B'), LengthsType()),
        }

    def __init__(self, sample_rate):
        super().__init__()
        self._sample_rate = sample_rate
        self.output = True
        self.signal = None
        self.signal_shape = None

    def __iter__(self):
        return self

    def __next__(self):
        if not self.output:
            raise StopIteration
        self.output = False
        return (torch.as_tensor(self.signal, dtype=torch.float32),
                torch.as_tensor(self.signal_shape, dtype=torch.int64))

    def set_signal(self, signal):
        self.signal = signal.astype(np.float32) / 32768.
        self.signal_shape = self.signal.size
        self.output = True

    def __len__(self):
        return 1


class FrameASR:

    def __init__(self, model_definition, asr_model, data_loader, data_layer,
                 frame_len=2.0, frame_overlap=2.5, offset=10):
        """
        Args:
          frame_len: frame's duration, seconds
          frame_overlap: duration of overlaps before and after current frame, seconds
          offset: number of symbols to drop for smooth streaming
        """
        self.asr_model = asr_model
        self.data_loader = data_loader
        self.data_layer = data_layer
        self.offset = offset

        sample_rate = model_definition['sample_rate']
        self.n_frame_len = int(frame_len * sample_rate)
        self.n_frame_overlap = int(frame_overlap * sample_rate)

        timestep_duration = model_definition['AudioToMelSpectrogramPreprocessor']['window_stride']
        for block in model_definition['JasperEncoder']['jasper']:
            timestep_duration *= block['stride'][0] ** block['repeat']
        self.n_timesteps_overlap = int(frame_overlap / timestep_duration) - 2
        self.buffer = np.zeros(shape=2 * self.n_frame_overlap + self.n_frame_len,
                               dtype=np.float32)
        self.reset()

    @torch.no_grad()
    def transcribe(self, frame=None):
        if frame is None:
            frame = np.zeros(shape=self.n_frame_len, dtype=np.float32)
        if len(frame) < self.n_frame_len:
            frame = np.pad(frame, [0, self.n_frame_len - len(frame)], 'constant')
        unmerged = self._decode(frame)
        return unmerged

    def _decode(self, frame):
        assert len(frame) == self.n_frame_len
        self.buffer[:-self.n_frame_len] = self.buffer[self.n_frame_len:]
        self.buffer[-self.n_frame_len:] = frame
        logits = self._infer_signal(self.buffer).cpu().numpy()[0]
        decoded = logits[self.n_timesteps_overlap:-self.n_timesteps_overlap]
        return decoded[:len(decoded) - self.offset]

    # inference method for audio signal (single instance)
    def _infer_signal(self, signal):
        self.data_layer.set_signal(signal)
        batch = next(iter(self.data_loader))
        audio_signal, audio_signal_len = batch
        log_probs, _encoded_len, _predictions = self.asr_model.forward(
            input_signal=audio_signal.to(self.asr_model.device),
            input_signal_length=audio_signal_len.to(self.asr_model.device)
        )
        return log_probs

    # Reset frame_history and decoder's state
    def reset(self):
        self.buffer = np.zeros(shape=self.buffer.shape, dtype=np.float32)

