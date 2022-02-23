import nemo.collections.asr as nemo_asr
import numpy as np

import lsp_model
from beam_search import beam_search


def basic_transcribe(audio_file):
    ctc_output, alphabet = run_ctc_model(audio_file)
    lm = lsp_model.Model()

    result = beam_search(
        ctc=ctc_output,
        lm=lm,
        alphabet=alphabet,
        beam_width=30,
        alpha=5,
        beta=1.5,
        prune=0.0000000000000001
    )  # beam_width=25, alpha=0.30, beta=5

    print(result)
    print(lm.lsp_model.cache)
    lm.quit()


def run_ctc_model(audio_file):
    asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)
    logits = asr_model.transcribe([audio_file], logprobs=True)[0]

    return softmax(logits), list(asr_model.decoder.vocabulary)


def softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum(axis=-1).reshape([logits.shape[0], 1])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to audio file')

    args = parser.parse_args()
    basic_transcribe(args.path)
