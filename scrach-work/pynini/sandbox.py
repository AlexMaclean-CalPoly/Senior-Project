import ast
import tokenize
from typing import List

import pynini
# from nemo_text_processing.text_normalization.en.taggers.cardinal import CardinalFst
from nemo_text_processing.inverse_text_normalization.en.taggers.cardinal import CardinalFst
# from pynini.lib import pynutil
# from nemo_text_processing.text_normalization.normalize import Normalizer
from nemo_text_processing.text_normalization.token_parser import TokenParser
from pynini.lib import pynutil
#
from pynini.lib import utf8

CHAR = utf8.VALID_UTF8_CHAR
WHITE_SPACE = pynini.union(" ", "\t", "\n", "\r", u"\u00A0").optimize()

#
# NEMO_DIGIT = byte.DIGIT
# NEMO_LOWER = pynini.union(*string.ascii_lowercase).optimize()
# NEMO_UPPER = pynini.union(*string.ascii_uppercase).optimize()
# NEMO_ALPHA = pynini.union(NEMO_LOWER, NEMO_UPPER).optimize()
# NEMO_ALNUM = pynini.union(NEMO_DIGIT, NEMO_ALPHA).optimize()
# NEMO_HEX = pynini.union(*string.hexdigits).optimize()
# NEMO_NON_BREAKING_SPACE = u"\u00A0"
# NEMO_SPACE = " "
#
NOT_SPACE = pynini.difference(CHAR, WHITE_SPACE).optimize()


# NEMO_NOT_QUOTE = pynini.difference(CHAR, r'"').optimize()
#
# NEMO_PUNCT = pynini.union(*map(pynini.escape, string.punctuation)).optimize()
# NEMO_GRAPH = pynini.union(NEMO_ALNUM, NEMO_PUNCT).optimize()


def token(type, fst):
    return pynutil.insert(f'tokens {{ {type}: "') + fst + pynutil.insert('" } ')


def get_number_fst():
    number_fst = CardinalFst().fst
    return number_fst


def space_star(x):
    delete_space = pynutil.delete(WHITE_SPACE)
    return pynutil.add_weight(x, 0.8) + pynutil.add_weight(
        pynini.closure(delete_space + pynutil.add_weight(x, 0.9)), 1.2)


other_tokens = [
    ('.', 'dot'),
    ('-', 'minus'),
    ('+', 'plus'),
    ('*', 'star'),
    ('*', 'times'),
    ('=', 'equals'),
    ('+=', 'plus equals'),
    ('(', 'open paren'),
    (')', "close paren"),
    (':', 'colon'),
    (',', 'comma'),
    ('/', 'slash')

]


def main():
    number_fst = get_number_fst()

    true_fst = pynini.cross('true', 'True')
    false_fst = pynini.cross('false', 'False')
    none_fst = pynini.cross('none', 'None')
    basic_atoms = token('name', true_fst | false_fst | none_fst)

    delete_space = pynutil.delete(WHITE_SPACE)
    string_fst = token('string',
                       pynini.cross('quote', "'") + delete_space +
                       pynini.closure(CHAR) +
                       delete_space + pynini.cross('unquote', "'"))

    underscore = pynini.cross(pynini.union('bar', 'underbar'), '_')
    id_part = (
            pynutil.add_weight(underscore, 0.9) |
            pynutil.add_weight(pynini.closure(NOT_SPACE), 1.1))
    id_fst = id_part + pynini.closure(delete_space + underscore + pynini.closure(delete_space + id_part, upper=1))
    id_complete = token('name', id_fst)

    # New Line Stuff
    newlines = (
            pynini.cross('next', token('newline', pynini.escape('\\n'))) |
            pynini.cross('then', token('newline', pynini.escape('\\n')) + token('indent', pynini.escape('\\t')))
    )

    # n = InverseNormalizer(lang='en')
    op_fst = pynini.union(*[
        token('op', pynini.cross(speech_value, py_value))
        for py_value, speech_value in other_tokens
    ])

    fun_def = (
            pynini.cross(
                pynini.union('define', 'def') +
                (pynini.closure(pynini.closure(pynini.union(' a', ' the'), upper=1) + ' function', upper=1)),
                token('name', 'def')
            )
            + delete_space + id_complete + delete_space +
            pynini.cross(pynini.union('of', 'taking', 'which takes'), token('op', '('))
            + delete_space + space_star(op_fst | basic_atoms | number_fst | string_fst | id_complete)
            + delete_space + pynini.cross('then', token('op', ')') + token('op', ':') +
                                          token('newline', pynini.escape('\\n')) + token('indent', pynini.escape('\\t')))
    )

    atom = fun_def | op_fst | newlines | basic_atoms | number_fst | string_fst | id_complete
    graph = space_star(atom).optimize()

   # fun_def.draw('fd.dot', width=6, height=3)


    p = TokenParser()

    while True:
        try:
            exp_str = input('exp: ')
            if exp_str == 'q':
                quit(0)

            r = exp_str @ graph
            path = pynini.shortestpath(r).string()
            print(path)
            p(path)
            print(python_verbalize(p.parse()))
        except Exception:
            print('error')


PYTHON_TOKEN_TYPES = {
    'name': tokenize.NAME,
    'string': tokenize.STRING,
    'op': tokenize.OP,
    'indent': tokenize.INDENT,
    'dedent': tokenize.DEDENT,
    'newline': tokenize.NEWLINE
}


def python_verbalize(tokens_dict: List[dict]):
    tokens = []
    for token_dict in tokens_dict:
        entry = token_dict['tokens']

        if len(entry) != 1:
            raise Exception('what')

        token_ty, token_string = entry.popitem()
        tokens.append((PYTHON_TOKEN_TYPES[token_ty], ast.literal_eval(f'"{token_string}"')))

    return tokenize.untokenize(tokens)


def token_test(path):
    with tokenize.open(path) as f:
        tokens = tokenize.generate_tokens(f.readline)
        t2 = [(info.type, info.string) for info in list(tokens)]
        print(tokenize.untokenize(t2))


if __name__ == '__main__':
    # token_test('../../project/beam_search.py')
    main()


# def add bar numbers open paren x comma y comma z close paren colon then return x plus y plus z