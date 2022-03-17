import json
import pprint

from nemo_text_processing.inverse_text_normalization.inverse_normalize import InverseNormalizer
from nemo_text_processing.text_normalization.normalize import Normalizer
import pynini
import tokenize

normalizer = Normalizer(input_case='cased', lang='en', whitelist='basic_rules.tsv')
inverse_normalizer = InverseNormalizer(lang='en')


# python -> text
def normalize(path):
    with tokenize.open(path) as f:
        tokens = tokenize.generate_tokens(f.readline)
        new_tokens = []
        for token in tokens:
            if token.type == tokenize.NEWLINE:
                new_tokens.append('<NEWLINE>')
            elif token.type == tokenize.INDENT:
                new_tokens.append('<INDENT>')
            elif token.type == tokenize.DEDENT:
                new_tokens.append('<DEDENT>')
            elif token.type == tokenize.NL:
                continue
            else:
                new_tokens.append(token.string)

    raw_text = " ".join(new_tokens)
    return normalizer.normalize(
        normalizer.normalize(raw_text, verbose=False),
    verbose=False)



            # if token.type == tokenize.

        # for token in tokens:
        #     print(token)



# text -> python
def inverse_normalize(text):
    pass


def read_file(path):
    with open(path, "r") as f:
        return f.read()

if __name__ == '__main__':
    # creates normalizer object that works on lower cased input
    text = normalize('../lsp_client.py')
    pp = pprint.PrettyPrinter()
    pp.pprint(text)


    # raw_text = read_file()
    # print(normalizer.normalize(raw_text, verbose=False))