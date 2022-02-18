
import os
from pathlib import PurePath


from lsp_client import LspClient, LspConnection

PYTHON_LSP = ['python', '-mpylsp']
PYTHON_LANG_ID = 'python'


class LspModel:
    def __init__(self) -> None:
        path = PurePath(os.getcwd())
        self.lang_client = LspClient(LspConnection(PYTHON_LSP), path)
        self.lang_client.initialize()
        self.doc_id = self.lang_client.did_open('buffer', PYTHON_LANG_ID, '')


    def get_completions(self, text) -> list[str]:
        self.lang_client.did_change(self.doc_id, text)
        response = self.lang_client.completion(self.doc_id, 0, len(text))
        results = [r['insertText'] for r in response['result']['items']]
        return results


    def quit(self) -> None:
        self.lang_client.shutdown()
        self.lang_client.exit()