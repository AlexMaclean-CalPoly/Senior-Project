import express from "express";
import { createServer } from "http";
import path from "path";
import { Server } from "socket.io";
import { fileURLToPath } from "url";
import TranscriptProcess from "./transcribe.js";

const app = express();
const server = createServer(app);
const io = new Server(server);

const __dirname = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

io.on("connection", (socket) => {
  console.log("a user connected");
  const transcriptProcess = new TranscriptProcess();

  transcriptProcess.onTranscript((data) => {
    console.log(`stdout: ${data}`);
    if (socket.connected) {
      socket.emit("transcript", data);
    }
  });

  socket.on("audio_in", (data) => {
    transcriptProcess.send(data);
  });

  socket.on("disconnect", () => {
    console.log("user disconnected");
    transcriptProcess.kill();
  });
});

server.listen(3000, () => {
  console.log("listening on 3000");
});
