console.log("loaded m.js");

constraints = {
  audio: true,
  video: false,
};

// function sendBlob(blob) {
//   var oReq = new XMLHttpRequest();
//   oReq.open("POST", "/a", true);
//   oReq.send(blob);

//   oReq.onload = function (oEvent) {
//     console.log(oReq.responseText);
//   };
// }

class MyWorkletNode extends AudioWorkletNode {
  constructor(context) {
    super(context, 'my-worklet-processor');
  }
}

const socket = new WebSocket('ws://localhost:8080');


navigator.mediaDevices
  .getUserMedia(constraints)
  .then((stream) => {
    const audioContext = new AudioContext();

    const microphone = audioContext.createMediaStreamSource(stream);
    console.log(microphone)

    const sampleRate = audioContext.sampleRate;
    console.log(sampleRate)


    let node
    audioContext.audioWorklet.addModule('../test2.js').then(() => {
      node = new AudioWorkletNode(audioContext, 'my-worklet-processor', {
        processorOptions: {
          someUsefulVariable: new Map([[1, 'one'], [2, 'two']]),
        }});
      console.log(node)
      node.port.postMessage(socket)
      microphone.connect(node)
    });


  })
  .catch(console.log);
