import pynini
from nemo_text_processing.text_normalization.token_parser import TokenParser


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
