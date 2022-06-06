import csv
from pathlib import Path

import pynini
from nemo_text_processing.text_normalization.en.taggers.cardinal import (
    CardinalFst,
)
from nemo_text_processing.text_normalization.en.taggers.decimal import (
    DecimalFst,
)
from pynini.lib import pynutil
from pynini.lib import utf8

CHAR = utf8.VALID_UTF8_CHAR
WHITE_SPACE = pynini.union(" ", "\t", "\n", "\r", "\u00A0").optimize()
NOT_SPACE = pynini.difference(CHAR, WHITE_SPACE).optimize()

maybe_delete_space = pynutil.delete(pynini.closure(WHITE_SPACE))
delete_space = pynutil.delete(pynini.closure(WHITE_SPACE, lower=1))
insert_space = pynutil.insert(" ")
delete_extra_space = pynini.cross(pynini.closure(WHITE_SPACE, 1), " ")
sigma = pynini.closure(CHAR)


def verb_fst():
    symbol = symbol_fst()
    cardinal = CardinalFst()
    cardinal_graph = cardinal.fst
    decimal = DecimalFst(cardinal, True)

    cardinal_final = ( cardinal_graph @
        (pynutil.delete('cardinal { ') +
    pynini.cross('negative: "true" ', "negative ").ques +
    pynutil.delete("integer: \"") +
    pynini.closure(CHAR) +
    pynutil.delete('" }')
    ))


    graph = pynini.closure(pynini.union(
        pynutil.add_weight(CHAR, 1),
        symbol,
        cardinal_final
    ))

    return graph


def symbol_fst():
    with open(Path(__file__).absolute().parent.parent / "racket_tagger" / "data" / "symbols.tsv", "r") as keywords_file:
        reader = csv.reader(keywords_file, delimiter="\t")
        keyword_mappings = [
            (row[1], row[0]) for row in reader
        ]

    graph = pynini.union(
        *[
            pynini.cross(pynini.escape(sym), insert_space + words + insert_space)
            for words, sym in keyword_mappings
        ]
    )
    return graph.optimize()


def main():

    f = verb_fst()

    with open("outfile.txt", 'w') as o:

        for fl in Path("./output").iterdir():
            if fl.suffix != ".txt":
                continue
            print(fl)

            with open(fl, 'r') as fl2:
                for line in fl2:
                    try:
                        text = pynini.shortestpath(pynini.escape(line) @ f).string()
                        print(text.lower(), file=o)
                    except Exception:
                        pass

if __name__ == "__main__":
    main()