import re
import nemo.collections.asr as nemo_asr
import numpy as np
import librosa
import os
# from ctc_decoders import Scorer


# class SneakyCustomScorer(Scorer):
#     def __init__(self, scorer) -> None:
#         pass

    # def get_log_cond_prob(self, arg):
    #     print(arg)
    #     return self.scorer.get_log_cond_prob(arg)

    # def get_sent_log_prob(self, arg):
    #     print(arg)
    #     return self.scorer.get_sent_log_prob(arg)


def softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum(axis=-1).reshape([logits.shape[0], 1])


def basic_transcribe(audio_file):
    print('')
    print("01@@@@@@@@@@@@@@@@")
    print('')
    asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)

    files = [audio_file]
    logits = asr_model.transcribe(files, logprobs=True)[0]
    probs = softmax(logits)
    print('')
    print("2@@@@@@@@@@@@@@@@")
    print('')
    print(probs)

    print('')
    print("3@@@@@@@@@@@@@@@@")
    print('')

    beam_search_lm = nemo_asr.modules.BeamSearchDecoderWithLM(
        vocab=list(asr_model.decoder.vocabulary),
        beam_width=16,
        alpha=2, beta=1.5,
        lm_path='lowercase_3-gram.pruned.1e-7.arpa',
        num_cpus=1,#max(os.cpu_count(), 1),
        input_tensor=False)


    print('')
    print("4@@@@@@@@@@@@@@@@")
    print('')
    # new_scorer = SneakyCustomScorer(beam_search_lm.scorer)

    #beam_search_lm.scorer.__class__ = SneakyCustomScorer

    print('')
    print("5@@@@@@@@@@@@@@@@")
    print('')

    o = beam_search_lm.forward(log_probs=np.expand_dims(probs, axis=0), log_probs_length=None)
    print('')
    print("@@@@@@@@@@@@@@@@")
    print('')

    print(o)



if __name__ == "__main__":
    import argparse
    print("00")

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to audio file')

    args = parser.parse_args()
    basic_transcribe(args.path)
