import json
import os
import re
import subprocess
from pathlib import PurePath
from collections import defaultdict

class LspConnection:
    def __init__(self, shell_args):
        self.process = subprocess.Popen(shell_args, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)

    def send(self, message):
        json_message = json.dumps(message)
        content_length = len(json_message)
        self.process.stdin.write(f'Content-Length: {content_length}\r\n\r\n{json_message}'.encode())
        self.process.stdin.flush()

    def receive(self):
        content_length = self._receive_headers()
        content = self.process.stdout.read(content_length)
        return json.loads(content)

    def _receive_headers(self):
        content_length = None
        while True:
            header = self.process.stdout.readline().decode()
            if header == '\r\n':
                return content_length
            match = re.match(r'Content-Length: *([0-9]+) *\r\n', header)
            if match:
                content_length = int(match.group(1))


class LspClient:
    def __init__(self, connection, root: PurePath):
        self.connection = connection
        self.root = root
        self.id = 1
        self.version_counter = defaultdict(int)
        self.messages = {None: []}

    def initialize(self):
        info = self._send_request("initialize", {
            "processId": os.getpid(),
            "rootPath": self.root.as_posix(),
            "rootUri": self.root.as_uri(),
            "capabilities": {}
        })
        print(info)

    def shutdown(self):
        self._send_request("shutdown")

    def exit(self):
        self._send_notification("exit")

    def did_open(self, document_path, lang_id, text):
        uri = self.root.joinpath(document_path).as_uri()
        self._send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": lang_id,
                "version": self.version_counter[uri],
                "text": text,
            }
        })
        return {'uri': uri}

    def did_change(self, document_id, text):
        self.version_counter[document_id['uri']] += 1
        self._send_notification("textDocument/didChange", {
            "textDocument": document_id | {'version': self.version_counter[document_id['uri']]},
            "contentChanges": [
                {
                    "text": text
                }
            ]
        })

    def completion(self, document_id, line, character):
        return self._send_request("textDocument/completion", {
            "textDocument": document_id,
            "position": {
                "line": line,
                "character": character
            }
        })

    def _send_notification(self, method, params=None):
        self._send(method, params, None)

    def _send_request(self, method, params=None):
        message_id = self.id
        self.id += 1
        self._send(method, params, message_id)
        return self._get_response(message_id)

    def _send(self, method: str, params, message_id):
        message = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params is not None:
            message['params'] = params
        if message_id is not None:
            message['id'] = message_id
        self.connection.send(message)

    def _get_response(self, message_id):
        while True:
            if message_id in self.messages:
                return self.messages[message_id]
            self._receive()

    def _receive(self):
        message = self.connection.receive()
        if 'id' in message:
            self.messages[message['id']] = message
        else:
            self.messages[None].append(message)

