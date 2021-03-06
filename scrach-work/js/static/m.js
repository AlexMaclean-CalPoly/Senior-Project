console.log("loaded m.js");

// Dynamically load socket.io
// var socketio, socket, stream;
// var script = document.createElement('script');
// script.setAttribute('src', 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.2/socket.io.min.js');
// script.setAttribute('integrity', 'sha384-toS6mmwu70G0fw54EGlWWeA4z3dyJ+dlXBtSURSKN4vyRFOcxd3Bzjj/AoOwY+Rg');
// script.setAttribute('crossorigin', 'anonymous');
// script.setAttribute("async", "false");
// let head = document.head;
// head.insertBefore(script, head.firstElementChild);

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

navigator.mediaDevices
  .getUserMedia(constraints)
  .then((stream) => {
    const audioContext = new AudioContext();

    const microphone = audioContext.createMediaStreamSource(stream);
    console.log(microphone);

    const sampleRate = audioContext.sampleRate;
    console.log(sampleRate);

    audioContext.audioWorklet.addModule("test2.js").then(() => {
      var streamWorkletNode = new StreamWorkletNode(audioContext, sampleRate);

      streamWorkletNode.port.onmessage = (event) => {
        // Send transformed PCM buffer to the server
        console.log(event.data);
        //socket.emit("audio_in", event.data);
      };

      // connect stream to our worklet
      microphone.connect(streamWorkletNode);
      // connect our worklet to the previous destination
      streamWorkletNode.connect(audioContext.destination);
    });

  })
  .catch(console.log);
