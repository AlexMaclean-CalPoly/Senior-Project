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

    def get_completions(self, text: str) -> list:
        self.lang_client.did_change(self.doc_id, text)
        response = self.lang_client.completion(self.doc_id, 0, len(text))
        results = [r['insertText'] for r in response['result']['items']]
        return results

    def score(self, prefix):
        return 1

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
        return (n_gram_score + lsp_score) / 2


if __name__ == "__main__":
    m = Model()
    m('this is a test')
