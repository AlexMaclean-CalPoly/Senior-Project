console.log("loaded main.js");

TARGET_SAMPLE_RATE = 16000;
TARGET_CHUNK_LENGTH = 1;

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

  set onaudio(callback) {
    this.port.onmessage = callback;
  }
}

function displayTranscript(transcript, parent) {
  parent.textContent = "";
  transcript.forEach((sexp) => {
    wrapper = document.createElement("div");
    parent.append(wrapper);
    displaySexp(sexp, wrapper);
  });
}

function displaySexp(sexp, parent) {
  if (Array.isArray(sexp)) {
    parent.append("(");
    sexp.forEach((innerSexp, index) => {
      if (index > 0) {
        parent.append(" ")
      }
      displaySexp(innerSexp, parent)
    });
    parent.append(")");
  } else {
    parent.append(codeNode(sexp.text, sexp.type))
  }
}

function codeNode(text, type) {
  node = document.createElement("span");
  node.textContent = text;
  node.classList.add(type);
  return node;
}

const recordButton = document.getElementById("record");
const outputText = document.getElementById("output");
const rawText = document.getElementById("raw");

const socket = io.connect();

socket.on("connection", () => {
  console.log("connection");
});

socket.on("disconnect", () => {
  console.log("disconnect");
});

socket.on("transcript", (data) => {
  console.log(data);
  displayTranscript(data.transcript, outputText)
  rawText.textContent = data.raw;
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
