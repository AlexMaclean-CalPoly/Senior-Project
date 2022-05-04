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

const socket = io.connect();

navigator.mediaDevices
  .getUserMedia(constraints)
  .then((stream) => {
    const audioContext = new AudioContext({ sampleRate: 16000 });

    const microphone = audioContext.createMediaStreamSource(stream);
    console.log(microphone);

    const sampleRate = audioContext.sampleRate;
    console.log(sampleRate);

    audioContext.audioWorklet.addModule("processors.js").then(() => {
      var streamWorkletNode = new StreamWorkletNode(audioContext, sampleRate);

      streamWorkletNode.port.onmessage = (event) => {
        // Send transformed PCM buffer to the server
        console.log(event.data);
        socket.emit("audio_in", event.data);
      };

      // connect stream to our worklet
      microphone.connect(streamWorkletNode);
      // connect our worklet to the previous destination
      streamWorkletNode.connect(audioContext.destination);
    });

  })
  .catch(console.log);
