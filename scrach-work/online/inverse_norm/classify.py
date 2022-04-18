import csv
import tokenize

import inverse_norm
from nemo_text_processing.inverse_text_normalization.en.taggers.cardinal import CardinalFst
from nemo_text_processing.inverse_text_normalization.en.taggers.decimal import DecimalFst
from pynini.lib import pynutil
from pynini.lib import utf8

CHAR = utf8.VALID_UTF8_CHAR
WHITE_SPACE = inverse_norm.union(" ", "\t", "\n", "\r", u"\u00A0").optimize()
NOT_SPACE = inverse_norm.difference(CHAR, WHITE_SPACE).optimize()

maybe_delete_space = pynutil.delete(inverse_norm.closure(WHITE_SPACE))
delete_space = pynutil.delete(inverse_norm.closure(WHITE_SPACE, lower=1))
insert_space = pynutil.insert(" ")
delete_extra_space = inverse_norm.cross(inverse_norm.closure(WHITE_SPACE, 1), " ")
sigma = inverse_norm.closure(CHAR)


class PyClassifyFst:
    def __init__(self):
        cardinal = CardinalFst()
        remove_and(cardinal)
        number = NumberFst(cardinal=cardinal)
        symbol = SymbolFst()
        basic = BasicFst(number=number, symbol=symbol)
        string = StringFst(basic=basic)
        name = NameFst(cardinal=cardinal)

        number_token = token(tokenize.NUMBER, number.fst)
        string_token = token(tokenize.STRING, string.fst)

        import_stmt = ImportStmtFst(name=name)

        stmt_fst = import_stmt.fst

        self.fst = string_token


class SymbolFst:
    def __init__(self) -> None:
        with open('data/symbols.tsv', 'r') as keywords_file:
            reader = csv.reader(keywords_file, delimiter="\t")
            keyword_mappings = [(row[0], row[1].split(' ')) for row in reader]

        self.fsts = {}
        for sym, words in keyword_mappings:
            fst = inverse_norm.cross(self._to_fst(words), inverse_norm.escape(sym))
            if sym in self.fsts:
                self.fsts[sym] = inverse_norm.union(self.fsts[sym], fst)
            else:
                self.fsts[sym] = fst

        self.fst = inverse_norm.union(*self.fsts.values())

    @staticmethod
    def _to_fst(words):
        result = inverse_norm.accep((words[0]))
        for word in words[1:]:
            result += delete_space + inverse_norm.accep(word)
        return result



class NumberFst:
    def __init__(self, cardinal: CardinalFst):
        decimal_graph = DecimalFst(cardinal).graph

        optional_minus_graph = inverse_norm.closure(
            inverse_norm.cross(inverse_norm.union("minus", "negative"), "-") + delete_space, 0, 1)

        optional_decimal_graph = inverse_norm.closure(
            delete_space + inverse_norm.cross("point", ".") + delete_space + decimal_graph, 0, 1)

        self.fst = optional_minus_graph + cardinal.graph_no_exception + optional_decimal_graph


class NameFst:
    def __init__(self, cardinal: CardinalFst) -> None:
        cardinal_graph = cardinal.graph_no_exception
        single_bar = inverse_norm.cross('bar', '_')
        bars = inverse_norm.closure(single_bar + delete_space)
        mid_bar = inverse_norm.cross(
            delete_space + inverse_norm.closure('bar' + delete_space, upper=1),
            '_') + bars

        word = inverse_norm.closure(NOT_SPACE, lower=1)
        word = (inverse_norm.project(word, "input") - 'bar') @ word

        g = (bars +
             inverse_norm.union(word + inverse_norm.closure(mid_bar + word), single_bar) +
             inverse_norm.closure(delete_space + single_bar))

        self.fst = g
        self.token = token(tokenize.NAME, self.fst)


class BasicFst:
    def __init__(self, number: NumberFst, symbol: SymbolFst):
        number_graph = number.fst
        symbol_graph = symbol.fst
        word_graph = inverse_norm.closure(NOT_SPACE, lower=1)

        token = (pynutil.add_weight(number_graph, 0.9) |
                 pynutil.add_weight(symbol_graph, 0.9) |
                 pynutil.add_weight(word_graph, 10))

        self.fst = token.optimize()


class StringFst:
    def __init__(self, basic: BasicFst):
        basic_graph = basic.fst

        token_graph = (inverse_norm.project(basic_graph, "input") - 'unquote') @ basic_graph

        graph = token_graph + inverse_norm.closure(delete_extra_space + token_graph)
        graph = (inverse_norm.cross("quote", "'") +
                 delete_space + graph + delete_space +
                 inverse_norm.cross("unquote", "'"))

        self.fst = graph.optimize()


class ImportStmtFst:
    def __init__(self, name: NameFst) -> None:
        t = {'.': token(tokenize.NAME, inverse_norm.cross('dot', '.')),
        'as': token(tokenize.NAME, 'as'),
        ',':  token(tokenize.NAME, inverse_norm.cross('and', ',')),
        'import': token(tokenize.NAME, 'import'),
        'from': token(tokenize.NAME, 'from'),
        '*': token(tokenize.OP, inverse_norm.cross(inverse_norm.union('star', 'all'), '*')),
        '(': token(tokenize.OP, pynutil.insert('(')),
        ')': token(tokenize.OP, pynutil.insert(')')),
        ' ': delete_extra_space,
        'NAME':  name.token
        }

        dotted_name = pynutil.join(t['NAME'], t[' '] + t['.'] + t[' '])
        dotted_as_name = dotted_name + inverse_norm.closure(t[' '] + t['as'] + t[' '] + t['NAME'], upper=1)
        dotted_as_names = pynutil.join(dotted_as_name, t[' '] + t[','] + t[' '])
        import_name = t['import'] + t[' '] + dotted_as_names

        import_from_as_name = t['NAME'] + inverse_norm.closure(t[' '] + t['as'] + t[' '] + t['NAME'], upper=1)
        import_from_as_names = pynutil.join(import_from_as_name, t[' '] + t[','] + t[' '])
        import_from_targets = (t['('] + import_from_as_names + t[')'] | t['*'])
        import_from = (t['from'] + t[' '] + dotted_name + t[' '] + t['import'] + t[' '] + import_from_targets)

        import_stmt = import_name | import_from
        self.fst = import_stmt


def token(type, fst):
    return pynutil.insert(f'tokens {{ type: "{type}" text: "') + fst + pynutil.insert('" } ')


def remove_and(cardinal: CardinalFst):
    graph = cardinal.graph_no_exception
    graph = (inverse_norm.cdrewrite(pynutil.delete("and"), WHITE_SPACE, WHITE_SPACE, sigma)
             @ graph)

    cardinal.graph_no_exception = graph
