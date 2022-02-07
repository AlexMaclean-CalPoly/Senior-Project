import os
from pathlib import PurePath

from lsp_client import LspClient, LspConnection

RACKET_LSP = ["racket", "-l", "racket-langserver"]
RACKET_LSP_SRC = ["racket", "racket-langserver/main.rkt"]
PYTHON_LSP = ['python', '-mpylsp']


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
    doc_id = lspc.did_open('test.py', 'python', '')
    lspc.completion(doc_id, 0, 0)
    lspc.shutdown()
    lspc.exit()


if __name__ == '__main__':
    path = PurePath(os.getcwd())
    python(path)


