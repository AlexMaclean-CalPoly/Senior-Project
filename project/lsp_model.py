import os
from pathlib import PurePath

import kenlm

from lsp_client import LspClient, LspConnection

PYTHON_LSP = ['python3', '-mpylsp']
PYTHON_LANG_ID = 'python'

KEN_LM_PATH = 'lowercase_3-gram.pruned.1e-7.arpa'


class LspModel:
    def __init__(self) -> None:
        path = PurePath(os.getcwd())
        self.lang_client = LspClient(LspConnection(PYTHON_LSP), path)
        self.lang_client.initialize()
        self.doc_id = self.lang_client.did_open('buffer', PYTHON_LANG_ID, '')
        self.cache = {}

    def get_completions(self, text: str) -> list:
        self.lang_client.did_change(self.doc_id, text)
        response = self.lang_client.completion(self.doc_id, 0, len(text))
        results = [r['insertText'] for r in response['result']['items']]
        return results

    def get_completions2(self, text: str):
        if text in self.cache:
            return self.cache[text]
        comps = self.get_completions(text)
        self.cache[text] = comps
        return comps

    def score(self, prefix: str):
        words = prefix.split()
        score = 0
        for i, word in enumerate(words):
            comps = self.get_completions2(" ".join(words[:i]) + " ")
            if word in comps:
                score += 1
        return score / len(words)

    def quit(self) -> None:
        self.lang_client.shutdown()
        self.lang_client.exit()


class Model:
    def __init__(self) -> None:
        self.n_gram_model = kenlm.Model(KEN_LM_PATH)
        self.lsp_model = LspModel()

    def __call__(self, prefix):
        n_gram_score = 10 ** self.n_gram_model.score(prefix, eos=False)
        lsp_score = self.lsp_model.score(prefix)
        return n_gram_score * 0.1 + lsp_score * 0.9

    def quit(self):
        self.lsp_model.quit()


if __name__ == "__main__":
    m = Model()
    m('this is a test')
