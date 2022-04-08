import pynini
from nemo_text_processing.text_normalization.token_parser import TokenParser

from classify import PyClassifyFst
from verbalizer import PyVerbalizer



class PyInverseNormalizer:
    def __init__(self):
        self.tagger = PyClassifyFst()
        self.parser = TokenParser()
        self.verbalizer = PyVerbalizer()

    def inverse_normalize(self, text: str, verbose: bool = False) -> str:
        lattice = self.find_tags(text)
        tagged_text = self.select_tag(lattice)
        if verbose:
            print(tagged_text)
        self.parser(tagged_text)
        tokens = self.parser.parse()
        return self.verbalizer.verbalize(tokens)

    def find_tags(self, text: str) -> 'pynini.FstLike':
        lattice = pynini.compose(text, self.tagger.fst)
        return lattice

    def select_tag(self, lattice: 'pynini.FstLike') -> str:
        lattice_stack = pynini.pdt_expand(pynini.project(lattice, 'output'), parens=self.tagger.parens)
        tagged_text = pynini.shortestpath(lattice_stack, nshortest=1, unique=True).string()
        return tagged_text
