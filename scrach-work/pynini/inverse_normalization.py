import ast
import csv
import tokenize
from typing import List

import pynini
# from nemo_text_processing.text_normalization.en.taggers.cardinal import CardinalFst
from nemo_text_processing.inverse_text_normalization.en.taggers.cardinal import CardinalFst
from nemo_text_processing.inverse_text_normalization.en.taggers.decimal import DecimalFst
# from pynini.lib import pynutil
from nemo_text_processing.text_normalization.normalize import Normalizer
from pynini.lib import pynutil
#
from pynini.lib import utf8
from black import format_str, FileMode
from nemo_text_processing.text_normalization.token_parser import TokenParser

CHAR = utf8.VALID_UTF8_CHAR
WHITE_SPACE = pynini.union(" ", "\t", "\n", "\r", u"\u00A0").optimize()
NOT_SPACE = pynini.difference(CHAR, WHITE_SPACE).optimize()
DELETE_SPACE = pynutil.delete(WHITE_SPACE)


PYTHON_TOKEN_TYPES = {
    'number': tokenize.NUMBER,
    'name': tokenize.NAME,
    'string': tokenize.STRING,
    'op': tokenize.OP,
    'indent': tokenize.INDENT,
    'dedent': tokenize.DEDENT,
    'newline': tokenize.NEWLINE
}


class PyInverseNormalizer:
    def __init__(self):
        self.parser = TokenParser()
        self.tagger = PyClassifyFst()

    def inverse_normalize(self, text: str, verbose: bool = False) -> str:
        lattice = self.find_tags(text)
        tagged_text = self.select_tag(lattice)
        if verbose:
            print(tagged_text)
        self.parser(tagged_text)
        tokens = self.parser.parse()
        return self.python_verbalize(tokens)

    def find_tags(self, text: str) -> 'pynini.FstLike':
        lattice = text @ self.tagger.fst
        return lattice

    def select_tag(self, lattice: 'pynini.FstLike') -> str:
        tagged_text = pynini.shortestpath(lattice, nshortest=1, unique=True).string()
        return tagged_text

    def python_verbalize(self, tokens_dict: List[dict]):
        tokens = []
        for token_dict in tokens_dict:
            entry = token_dict['tokens']

            if len(entry) != 1:
                raise Exception('what')

            token_ty, token_string = entry.popitem()
            tokens.append((PYTHON_TOKEN_TYPES[token_ty], ast.literal_eval(f'"{token_string}"')))

        return format_str(tokenize.untokenize(tokens), mode=FileMode())


class PyClassifyFst:
    def __init__(self):
        cardinal = CardinalFst()
        natural_graph = cardinal.graph_no_exception
        number_graph = token('number', NumberFst(cardinal=cardinal).fst)

        self.fst = number_graph


class KeywordFst:
    def __init__(self):
        with open('keywords.tsv', 'r') as keywords_file:
            reader = csv.reader(keywords_file, delimiter="\t")
            self._fsts = {keyword_mapping[0]: self._get_fst(keyword_mapping)
                          for keyword_mapping in reader}

        self.fst = pynini.union(*self._fsts)

    @staticmethod
    def _get_fst(keyword_mapping):
        keyword = keyword_mapping[0]
        return pynini.string_map(((kw.lower(), keyword)
                                  for kw in keyword_mapping))

    def __getitem__(self, index):
        return self._fsts[index]


class NumberFst:
    def __init__(self, cardinal):
        decimal_graph = DecimalFst(cardinal).graph

        optional_minus_graph = pynini.closure(
            pynini.cross(pynini.union("minus", "negative"), "-") + DELETE_SPACE, 0, 1)

        optional_decimal_graph = pynini.closure(
            DELETE_SPACE + pynini.cross("point", ".") + DELETE_SPACE + decimal_graph, 0, 1)

        self.fst = optional_minus_graph + cardinal.graph_no_exception + optional_decimal_graph




def token(type, fst):
    return pynutil.insert(f'tokens {{ {type}: "') + fst + pynutil.insert('" } ')


def get_number_fst():
    number_fst = CardinalFst().graph_no_exception
    optional_minus_graph = pynini.closure(pynini.cross(pynini.union("minus", "negative"), "-") + pynutil.delete(WHITE_SPACE), 0, 1)
    return optional_minus_graph + number_fst


def space_star(x):
    delete_space = pynutil.delete(WHITE_SPACE)
    return pynutil.add_weight(x, 0.8) + pynutil.add_weight(
        pynini.closure(delete_space + pynutil.add_weight(x, 0.9)), 1.2)


# def main():
#     keyword_fst = KeywordFst()
#
#
#     number_fst = get_number_fst()
#
#
#
#     atom = number_fst
#     graph = space_star(atom).optimize()
#
#     # fun_def.draw('fd.dot', width=6, height=3)
#
#
#    # p = TokenParser()




#  basic_atoms = token('name', true_fst | false_fst | none_fst)
#
#  delete_space = pynutil.delete(WHITE_SPACE)
#  string_fst = token('string',
#                     pynini.cross('quote', "'") + delete_space +
#                     pynini.closure(CHAR) +
#                     delete_space + pynini.cross('unquote', "'"))
#
#  underscore = pynini.cross(pynini.union('bar', 'underbar'), '_')
#  id_part = (
#          pynutil.add_weight(underscore, 0.9) |
#          pynutil.add_weight(pynini.closure(NOT_SPACE), 1.1))
#  id_fst = id_part + pynini.closure(delete_space + underscore + pynini.closure(delete_space + id_part, upper=1))
#  id_complete = token('name', id_fst)
#
#  # New Line Stuff
#  newlines = (
#          pynini.cross('next', token('newline', pynini.escape('\\n'))) |
#          pynini.cross('then', token('newline', pynini.escape('\\n')) + token('indent', pynini.escape('\\t')))
#  )
#
#  # n = InverseNormalizer(lang='en')
#  op_fst = pynini.union(*[
#      token('op', pynini.cross(speech_value, py_value))
#      for py_value, speech_value in other_tokens
#  ])
#
#  fun_def = (
#          pynini.cross(
#              pynini.union('define', 'def') +
#              (pynini.closure(pynini.closure(pynini.union(' a', ' the'), upper=1) + ' function', upper=1)),
#              token('name', 'def')
#          )
#          + delete_space + id_complete + delete_space +
#          pynini.cross(pynini.union('of', 'taking', 'which takes'), token('op', '('))
#          + delete_space + space_star(op_fst | basic_atoms | number_fst | string_fst | id_complete)
#          + delete_space + pynini.cross('then', token('op', ')') + token('op', ':') +
#                                        token('newline', pynini.escape('\\n')) + token('indent', pynini.escape('\\t')))
#  )
#
#  atom = fun_def | op_fst | newlines | basic_atoms | number_fst | string_fst | id_complete
#  graph = space_star(atom).optimize()
#
# # fun_def.draw('fd.dot', width=6, height=3)
#
#
#  p = TokenParser()
#



