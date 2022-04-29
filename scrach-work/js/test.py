# import librosa
#
# l = librosa.load('sample4.opus', res_type='kaiser_fast', sr=16000)
# print(l)


import opuslib
import librosa
OPUS_PCM_LEN_SIZE = 4
OPUS_RATE_SIZE = 4
OPUS_CHANNELS_SIZE = 1
OPUS_WIDTH_SIZE = 1
OPUS_CHUNK_LEN_SIZE = 2

# l =librosa.load('sample4.opus', sr=16000)
# print(l)

OPUS_CHUNK_LEN_SIZE = 2


def unpack_number(data):
    return int.from_bytes(data, 'big', signed=False)


def get_opus_frame_size(rate):
    return 60 * rate // 1000

def read_opus_header(opus_file):
    opus_file.seek(0)
    pcm_buffer_size = unpack_number(opus_file.read(OPUS_PCM_LEN_SIZE))
    rate = unpack_number(opus_file.read(OPUS_RATE_SIZE))
    channels = unpack_number(opus_file.read(OPUS_CHANNELS_SIZE))
    width = unpack_number(opus_file.read(OPUS_WIDTH_SIZE))
    return pcm_buffer_size, (rate, channels, width)

def read_opus(opus_file):
    pcm_buffer_size, audio_format = read_opus_header(opus_file)
    print(audio_format)
    print(pcm_buffer_size)
    rate, channels, _ = audio_format
    frame_size = get_opus_frame_size(rate)
    import opuslib
    decoder = opuslib.Decoder(rate, channels)
    audio_data = bytearray()
    while len(audio_data) < pcm_buffer_size:
        chunk_len = unpack_number(opus_file.read(OPUS_CHUNK_LEN_SIZE))
        chunk = opus_file.read(chunk_len)
        decoded = decoder.decode(chunk, frame_size)
        audio_data.extend(decoded)
    audio_data = audio_data[:pcm_buffer_size]
    return audio_format, audio_data


with open('outo.opus', 'rb') as f:
    o = read_opus(f)

# print(len(raw))
# d =  opuslib.Decoder(fs= 48000, channels=1)
# o = d.decode(raw, frame_size=960)

print(o)