import nemo.collections.asr as nemo_asr
import numpy as np
import librosa
import os


def softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum(axis=-1).reshape([logits.shape[0], 1])


def basic_transcribe(audio_file):
    asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)

    files = [audio_file]
    logits = asr_model.transcribe(files, logprobs=True)[0]
    probs = softmax(logits)
    print(probs)

    beam_search_lm = nemo_asr.modules.BeamSearchDecoderWithLM(
        vocab=list(asr_model.decoder.vocabulary),
        beam_width=16,
        alpha=2, beta=1.5,
        lm_path='',
        num_cpus=max(os.cpu_count(), 1),
        input_tensor=False)

    beam_search_lm.forward(log_probs=np.expand_dims(probs, axis=0), log_probs_length=None)


# 20ms is duration of a timestep at output of the model
# time_stride = 0.02


# labels = list(asr_model.decoder.vocabulary) + ['blank']

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to audio file')

    args = parser.parse_args()
    basic_transcribe(args.path)
