import re
import nemo.collections.asr as nemo_asr
import numpy as np
import librosa
import os
from beam_search import beam_search


# (Scorer)
class SneakyCustomScorer:
    def __init__(self, scorer) -> None:
        self.scorer = scorer

    def get_log_cond_prob(self, arg):
        print(arg)
        return self.scorer.get_log_cond_prob(arg)

    def get_sent_log_prob(self, arg):
        print(arg)
        return self.scorer.get_sent_log_prob(arg)


def softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum(axis=-1).reshape([logits.shape[0], 1])


def run_ctc_model(audio_file):
    asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)

    logits = asr_model.transcribe([audio_file], logprobs=True)[0]
    return softmax(logits)


def basic_transcribe(audio_file):
    ctc_output = run_ctc_model(audio_file)

    result = beam_search(
        ctc=ctc_output,

        #vocab=list(asr_model.decoder.vocabulary),
        k=16, # beam_width
        alpha=2,
        beta=1.5,
        )

    print(result)

        #lm_path='lowercase_3-gram.pruned.1e-7.arpa',


    # new_scorer = SneakyCustomScorer(beam_search_lm.scorer)
    # beam_search_lm.scorer = new_scorer

    # o = beam_search_lm.forward(log_probs=np.expand_dims(probs, axis=0), log_probs_length=None)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to audio file')

    args = parser.parse_args()
    basic_transcribe(args.path)
