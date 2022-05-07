import path from "path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

class TranscriptProcess {
  constructor() {
    this.process = spawn("python", [path.join(__dirname, "python", "main.py")]);
  }

  send(data) {
    if (this.process.stdin.writable) {
      this.process.stdin.write(data);
    }
  }

  onTranscript(callback) {
    this.process.stdout.on("data", callback);
  }

  kill() {
    this.process.kill();
  }
}

export default TranscriptProcess;
