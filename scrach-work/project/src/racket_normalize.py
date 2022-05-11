import pynini
from nemo_text_processing.text_normalization.token_parser import TokenParser
from pathlib import Path


class InverseNormalizer:
    def __init__(self, tagger: pynini.FstLike, verbalizer):
        self.tagger = tagger
        self.parser = TokenParser()
        self.verbalizer = verbalizer

    def inverse_normalize(self, text: str, verbose: bool = False) -> str:
        lattice = self.find_tags(text)
        tagged_text = self.select_tag(lattice)
        if verbose:
            print(tagged_text)
        self.parser(tagged_text)
        tokens = self.parser.parse()
        return self.verbalizer.verbalize(tokens)

    def find_tags(self, text: str) -> pynini.FstLike:
        lattice = text @ self.tagger
        return lattice

    @staticmethod
    def select_tag(lattice: pynini.FstLike) -> str:
        tagged_text = pynini.shortestpath(lattice, nshortest=1, unique=True).string()
        return tagged_text


class RacketVerbalize:
    def verbalize(self, raw_tokens):
        tokens = [entry["tokens"] for entry in raw_tokens]
        stack = [[]]
        for token in tokens:
            top = stack[-1]
            ty, text = token["type"], token["text"]
            if ty == "atom":
                top.append(token["text"])
            elif ty == "op" and text == "of":
                new = [] if token.get("group", "0") == "1" else [top.pop()]
                top.append(new)
                stack.append(new)
            elif ty == "op" and text == "next":
                stack.pop()

        return "\n".join(self.print_sexp(entry) for entry in stack[0])

    @staticmethod
    def print_sexp(sexp):
        if isinstance(sexp, list):
            return ['('] + [f for entry in sexp for f in RacketVerbalize.print_sexp(entry)] + [')']
        else:
            return sexp


def racket_inverse_normalizer():
    tagger = pynini.Fst.read(Path(__file__).parent / "racket.fst")
    return InverseNormalizer(tagger, RacketVerbalize())
