import pynini
from nemo_text_processing.text_normalization.token_parser import TokenParser

from classify import PyClassifyFst
from verbalizer import PyVerbalizer


def select_tag(lattice: 'pynini.FstLike') -> str:
    tagged_text = pynini.shortestpath(lattice, nshortest=1, unique=True).string()
    return tagged_text


class PyInverseNormalizer:
    def __init__(self):
        self.tagger = PyClassifyFst()
        self.parser = TokenParser()
        self.verbalizer = PyVerbalizer()

    def pyninialize(self, text: str, verbose: bool = False) -> str:
        lattice = self.find_tags(text)
        tagged_text = select_tag(lattice)
        if verbose:
            print(tagged_text)
        self.parser(tagged_text)
        tokens = self.parser.parse()
        return self.verbalizer.verbalize(tokens)

    def find_tags(self, text: str) -> 'pynini.FstLike':
        lattice = text @ self.tagger.fst
        return lattice
