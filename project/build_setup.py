# Run in the Docker build step,
# not necessary but helps make the run a bit faster

import nemo.collections.asr as nemo_asr

nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)