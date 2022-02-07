print('a')

import nemo.collections.asr as nemo_asr
import numpy as np
import librosa


print('a')
asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)
print(asr_model)