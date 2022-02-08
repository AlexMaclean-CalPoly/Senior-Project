import os
from pathlib import PurePath
import pprint

from lsp_client import LspClient, LspConnection

RACKET_LSP = ["racket", "-l", "racket-langserver"]
RACKET_LSP_SRC = ["racket", "racket-langserver/main.rkt"]
PYTHON_LSP = ['python', '-mpylsp']

pp = pprint.PrettyPrinter(indent=4)


def racket(path):
    lspc = LspClient(LspConnection(RACKET_LSP), path)
    lspc.initialize()
    doc_id = lspc.did_open('test.rkt', 'racket', '#lang racket')
    lspc.completion(doc_id, 1, 2)
    lspc.shutdown()
    lspc.exit()


def python(path):
    lspc = LspClient(LspConnection(PYTHON_LSP), path)
    lspc.initialize()
    doc_id = lspc.did_open('test.py', 'python', 'import ')
    response = lspc.completion(doc_id, 0, 20)
    results = [r['insertText'] for r in response['result']['items']]
    pp.pprint(results)
    lspc.shutdown()
    lspc.exit()


if __name__ == '__main__':
    path = PurePath(os.getcwd())
    python(path)


