
from sympy import im


from lsp_client import LspClient, LspConnection

class LspModel:
    def __init__(self) -> None:
        lspc = LspClient(LspConnection(RACKET_LSP), path)
        lspc.initialize()
        doc_id = lspc.did_open('test.rkt', 'racket', '#lang racket')
        lspc.completion(doc_id, 1, 2)
        lspc.shutdown()
        lspc.exit()