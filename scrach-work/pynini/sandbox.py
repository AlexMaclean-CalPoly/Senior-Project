import tokenize
from inverse_normalization import PyInverseNormalizer
from nemo_text_processing.inverse_text_normalization import inverse_normalize


def main():
    pin = PyInverseNormalizer()
    while True:
        try:
            exp_str = input('exp: ')
            if exp_str == 'q':
                quit(0)
            o = pin.inverse_normalize(exp_str)
            print(o)

        except Exception:
            print('error')


# def token_test(path):
#     with tokenize.open(path) as f:
#         tokens = tokenize.generate_tokens(f.readline)
#         t2 = [(info.type, info.string) for info in list(tokens)]
#         print(tokenize.untokenize(t2))


if __name__ == '__main__':
    # token_test('../../project/beam_search.py')
    main()
