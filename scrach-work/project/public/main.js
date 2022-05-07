console.log("loaded main.js");

constraints = {
  audio: true,
  video: false,
};

class StreamWorkletNode extends AudioWorkletNode {
  constructor(context, sampleRate) {
    super(context, "stream-processor", {
      processorOptions: {
        sampleRate: sampleRate,
      },
    });
  }
}

const recordButton = document.getElementById("record");
const outputText = document.getElementById("output");

const socket = io.connect();
var enc = new TextDecoder("utf-8");

socket.on("transcript", (data) => {
  text = enc.decode(data);
  outputText.textContent = text;
  console.log(text);
});

navigator.mediaDevices
  .getUserMedia(constraints)
  .then((stream) => {
    recordButton.onclick = () => {
      const audioContext = new AudioContext({ sampleRate: 16000 });

      const microphone = audioContext.createMediaStreamSource(stream);
      console.log(microphone);

      const sampleRate = audioContext.sampleRate;
      console.log(sampleRate);

      audioContext.audioWorklet.addModule("processors.js").then(() => {
        var streamWorkletNode = new StreamWorkletNode(audioContext, sampleRate);

        streamWorkletNode.port.onmessage = (event) => {
          socket.emit("audio_in", event.data);
        };

        microphone.connect(streamWorkletNode);
        streamWorkletNode.connect(audioContext.destination);
      });
    };
  })
  .catch(console.error);
