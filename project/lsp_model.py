import os
from pathlib import PurePath

from lsp_client import LspClient, LspConnection

import kenlm

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

    def quit(self) -> None:
        self.lang_client.shutdown()
        self.lang_client.exit()


class Model:
    def __init__(self) -> None:
        self.n_gram_model = kenlm.Model(KEN_LM_PATH)
        self.lsp_model = LspModel()


    def score(self):
        n_gram_score = self.n_gram_model.score('this is a sentence .', bos=True, eos=True)
        print(n_gram_score)


if __name__ == "__main__":
    m = Model()
    m.score()
