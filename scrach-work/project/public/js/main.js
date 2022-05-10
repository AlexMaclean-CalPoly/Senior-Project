console.log("loaded main.js");

TARGET_SAMPLE_RATE = 16000;
TARGET_CHUNK_LENGTH = 0.1;

constraints = {
  audio: true,
  video: false,
};

class StreamWorkletNode extends AudioWorkletNode {
  constructor(context, targetChunkLength) {
    super(context, "stream-processor", {
      processorOptions: { targetChunkLength },
    });
  }
}

const recordButton = document.getElementById("record");
const outputText = document.getElementById("output");

const socket = io.connect();
const enc = new TextDecoder("utf-8");

socket.on("connection", () => {
  console.log("connected");
})

socket.on("disconnect", () => {
  console.log("disconnected");
})

socket.on("transcript", (data) => {
  text = enc.decode(data);
  outputText.textContent = text;
  console.log(text);
});

navigator.mediaDevices
  .getUserMedia(constraints)
  .then((stream) => {
    recordButton.onclick = () => {
      const audioContext = new AudioContext({ sampleRate: TARGET_SAMPLE_RATE });

      const microphone = audioContext.createMediaStreamSource(stream);
      const sampleRate = audioContext.sampleRate;
      console.log(sampleRate);

      audioContext.audioWorklet.addModule("js/processors.js").then(() => {
        var streamWorkletNode = new StreamWorkletNode(
          audioContext,
          TARGET_CHUNK_LENGTH
        );

        streamWorkletNode.port.onmessage = (event) => {
          socket.emit("audio_in", event.data);
        };

        microphone.connect(streamWorkletNode);
        streamWorkletNode.connect(audioContext.destination);
      });
    };
  })
  .catch(console.error);
