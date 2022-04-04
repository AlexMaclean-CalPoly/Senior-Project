import csv
import tokenize

import pynini
from nemo_text_processing.inverse_text_normalization.en.taggers.cardinal import CardinalFst
from nemo_text_processing.inverse_text_normalization.en.taggers.decimal import DecimalFst
from pynini.lib import pynutil
from pynini.lib import utf8

CHAR = utf8.VALID_UTF8_CHAR
WHITE_SPACE = pynini.union(" ", "\t", "\n", "\r", u"\u00A0").optimize()
NOT_SPACE = pynini.difference(CHAR, WHITE_SPACE).optimize()

delete_space = pynutil.delete(pynini.closure(WHITE_SPACE))
insert_space = pynutil.insert(" ")
delete_extra_space = pynini.cross(pynini.closure(WHITE_SPACE, 1), " ")
sigma = pynini.closure(CHAR)


class PyClassifyFst:
    def __init__(self):
        cardinal = CardinalFst()
        remove_and(cardinal)
        number = NumberFst(cardinal=cardinal)
        basic = BasicFst(number=number)
        string = StringFst(basic=basic)

        number_token = token(tokenize.NUMBER, number.fst)
        string_token = token(tokenize.STRING, string.fst)

        self.fst = number_token | string_token


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
            pynini.cross(pynini.union("minus", "negative"), "-") + delete_space, 0, 1)

        optional_decimal_graph = pynini.closure(
            delete_space + pynini.cross("point", ".") + delete_space + decimal_graph, 0, 1)

        self.fst = optional_minus_graph + cardinal.graph_no_exception + optional_decimal_graph


class StringFst:
    def __init__(self, basic):
        basic_graph = basic.fst

        token_graph = (pynini.project(basic_graph, "input") - 'unquote') @ basic_graph

        graph = token_graph + pynini.closure(delete_extra_space + token_graph)
        graph = (pynini.cross("quote", "'") +
                 delete_space + graph + delete_space +
                 pynini.cross("unquote", "'"))

        self.fst = graph.optimize()


class BasicFst:
    def __init__(self, number):
        number_graph = number.fst
        word_graph = pynini.closure(NOT_SPACE, lower=1)

        token = (pynutil.add_weight(number_graph, 0.9) |
                 pynutil.add_weight(word_graph, 1.1))

        self.fst = token.optimize()


def token(type, fst):
    return pynutil.insert(f'tokens {{ type: "{type}" text: "') + fst + pynutil.insert('" } ')


def remove_and(cardinal):
    graph = cardinal.graph_no_exception
    graph = (pynini.cdrewrite(pynutil.delete("and"), WHITE_SPACE, WHITE_SPACE, sigma)
             @ graph)

    cardinal.graph_no_exception = graph
