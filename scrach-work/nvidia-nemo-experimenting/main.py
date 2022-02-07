import nemo.collections.asr as nemo_asr
import numpy as np
import librosa

AUDIO_FILENAME = "./test-audio-2.wav" # the unprocessed audio breaks the model

def softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum(axis=-1).reshape([logits.shape[0], 1])


asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)

files = [AUDIO_FILENAME]
transcript = asr_model.transcribe(paths2audio_files=files)[0]
print(f'Transcript: "{transcript}"')


logits = asr_model.transcribe(files, logprobs=True)[0]
probs = softmax(logits)
print(probs)

# 20ms is duration of a timestep at output of the model
time_stride = 0.02


labels = list(asr_model.decoder.vocabulary) + ['blank']