import tokenize
from inverse_normalization import PyInverseNormalizer
#from nemo_text_processing.inverse_text_normalization import inverse_normalize
import pynini
from pynini.lib import byte, rewrite



def main():
    pin = PyInverseNormalizer()
    while True:
        try:
            exp_str = input('exp: ')
            if exp_str == 'q':
                quit(0)
            o = pin.inverse_normalize(exp_str.strip(), verbose=True)
            print(o)

        except Exception:
            print('error')


def token_test(path):
    with tokenize.open(path) as f:
        tokens = list(tokenize.generate_tokens(f.readline))
        for token in tokens:
            print(token)
        t2 = [(info.type, info.string) for info in list(tokens)]
        print('a:')
        print(tokenize.untokenize(t2))


if __name__ == '__main__':
    token_test('test.py')
    main()

# #
# _sigma_star = pynini.closure(byte.BYTE)
# # _tolower = pynini.cdrewrite(pynini.cross('s', 'z'), "a", "b", _sigma_star)
# # pynini.replace()
#
# myrule0 = pynini.cross('Hello $TEST', 'goodbye $TEST')
# t = pynini.cdrewrite(pynini.cross('$TEST', pynini.cross('a', 'b')), "", "", _sigma_star)
# myrule =  myrule0 @ t
#
# print(pynini.shortestpath(myrule).string())
# print(rewrite.top_rewrite('Hello $TEST', myrule))