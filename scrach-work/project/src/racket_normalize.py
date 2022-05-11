from lib2to3.pgen2 import token
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
        tagged_text = self.select_tag(lattice, text)
        if verbose:
            print(tagged_text)
        tokens = self.parse(tagged_text)
        return self.verbalizer(tokens)

    def find_tags(self, text: str) -> pynini.FstLike:
        lattice = text @ self.tagger
        return lattice

    def parse(self, tagged_text):
        if tagged_text == "":
            return []
        self.parser(tagged_text)
        return self.parser.parse()

    @staticmethod
    def select_tag(lattice: pynini.FstLike, text) -> str:
        try:
            tagged_text = pynini.shortestpath(lattice, nshortest=1, unique=True).string()
            return tagged_text
        except Exception:
            print(f'AAAAAAA {text}')


ATOMS = {'name', 'string', 'number'}

class RacketVerbalize:
    def __call__(self, raw_tokens):
        tokens = [entry["tokens"] for entry in raw_tokens]
        stack = [[]]
        for token in tokens:
            top = stack[-1]
            ty, text = token["type"], token["text"]
            if ty in ATOMS:
                top.append({'text': self.format_atom_text(text, ty), 'type': ty})
            elif ty == "op" and text == "of":
                new = [] if token.get("group", "0") == "1" else [top.pop()]
                top.append(new)
                stack.append(new)
            elif ty == "op" and text == "next":
                if len(stack) > 1:
                    stack.pop()

        return stack[0]
        #return "\n".join(self.print_sexp(entry) for entry in stack[0])

    @staticmethod
    def format_atom_text(text, ty):
        if ty == "string":
            return f'"{text}"'
        return text


    @staticmethod
    def print_sexp(sexp):
        if isinstance(sexp, list):
            return f'({" ".join(RacketVerbalize.print_sexp(entry) for entry in sexp)})'
        else:
            return sexp


def racket_inverse_normalizer():
    tagger = pynini.Fst.read(Path(__file__).parent / "racket.fst")
    return InverseNormalizer(tagger, RacketVerbalize())
