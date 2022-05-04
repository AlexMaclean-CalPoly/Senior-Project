console.log("loaded index.js");

const express = require("express");
const http = require("http");
const path = require("path");
const { Server } = require("socket.io");
const { spawn } = require("node:child_process");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, "static")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "static", "index.html"));
});

io.on("connection", (socket) => {
  console.log("a user connected");

  const ls = spawn("python", [path.join(__dirname, "python", "main.py")]);

  ls.stdout.on("data", (data) => {
    console.log(`stdout: ${data}`);
    socket.emit("transcript", data);
  });

  socket.on("audio_in", (data) => {
    ls.stdin.write(data);
  });

  socket.on("disconnect", () => {
    console.log("user disconnected");
  });
});

server.listen(3000, () => {
  console.log("listening on *:3000");
});
