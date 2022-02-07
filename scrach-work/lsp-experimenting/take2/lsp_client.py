import json
import os
import re
import subprocess
from pathlib import Path


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
        length_part = self.process.stdout.readline().decode()
        match = re.match(r'Content-Length: *([0-9]+) *\r\n', length_part)
        content_length = int(match.group(1))
        content = self.process.stdout.read(2 + content_length)
        return json.loads(content)


class LspClient:
    def __init__(self, connection):
        self.connection = connection

    def initialize(self, root: Path):
        self._send("initialize", {
            "processId": os.getpid(),
            "rootPath": root.as_posix(),
            "rootUri": root.as_uri(),
            "capabilities": {}
        })
        response = self.connection.receive()
        print(response)

    def shutdown(self):
        self._send("shutdown", {})
        response = self.connection.receive()
        print(response)

    def _send(self, method, params):
        self.connection.send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        })


if __name__ == '__main__':
    lspc = LspClient(LspConnection(["racket", "-l", "racket-langserver"]))
    path = Path(os.getcwd())
    lspc.initialize(path)
    lspc.shutdown()
