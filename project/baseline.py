import nemo.collections.asr as nemo_asr


def basic_transcribe(audio_file):
    asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name='QuartzNet15x5Base-En', strict=False)

    files = [audio_file]
    transcript = asr_model.transcribe(paths2audio_files=files)[0]
    print(f'Transcript: "{transcript}"')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to audio file')

    args = parser.parse_args()
    basic_transcribe(args.path)
