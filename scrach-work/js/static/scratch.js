// <!-- <script src="https://unpkg.com/extendable-media-recorder@6.6.3/build/es5/bundle.js"></script> -->
// <!-- <script src="https://unpkg.com/extendable-media-recorder-wav-encoder@7.0.67/build/es5/bundle.js"></script> -->

// <!-- <script type="module">
//   import exr from "https://dev.jspm.io/npm:extendable-media-recorder";
//   import exrWav from "https://dev.jspm.io/npm:extendable-media-recorder-wav-encoder";

//   console.log(exr);
//   console.log(exrWav);

//   const { MediaRecorder, register } = exr;
//   const { connect } = exrWav;

//   async function sendBlob(blob) {
//     var oReq = new XMLHttpRequest();
//     oReq.open("POST", "/a", true);
//     oReq.send(blob);

//     oReq.onload = function (oEvent) {
//       console.log(oReq.responseText);
//     };
//   }

//   // await register(await connect());

//   // const stream = await navigator.mediaDevices.getUserMedia({
//   //   audio: { channelCount: { exact: 1 }, sampleRate: { ideal: 16000 } },
//   //   video: false,
//   // });
//   // const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/wav" });

//   // mediaRecorder.start(500);

//   // mediaRecorder.ondataavailable = async (e) => {
//   //   const text = await e.data.text();
//   //   sendBlob(text).then((b) => {
//   //     console.log(b);
//   //   });
//   // };

//   //import exr from 'https://dev.jspm.io/npm:extendable-media-recorder';
//   // import { MediaRecorder, register } from 'https://dev.jspm.io/npm:extendable-media-recorder';
//   // import { connect } from 'https://dev.jspm.io/npm:extendable-media-recorder-wav-encoder';

//   // await register(await connect());

//   // const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//   // const mediaRecoder = new MediaRecorder(stream, { mimeType: 'audio/wav' });

//   // async function main(){

//   //   await register(await connect());

//   //   const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//   //   const mediaRecoder = new MediaRecorder(stream, { mimeType: 'audio/wav' });
//   // }

//   // main()

//   navigator.mediaDevices
//     .getUserMedia({
//       audio: { channelCount: { exact: 1 }, sampleRate: { ideal: 16000 } },
//       video: false,
//     })
//     .then((stream) => {
//       const sampleRate = stream.getAudioTracks()[0].getSettings().sampleRate;
//       console.log(sampleRate);
//       const recorder = new MediaRecorder(stream);
//       recorder.start(2000);

//       recorder.ondataavailable = async (e) => {
//         console.log(e.data);
//         sendBlob(e.data).then((b) => {
//           // console.log(e.data.text())
//           console.log(b);
//         });
//       };

//       // recorder.onstart = async () => {
//       //   await fetch("/stream/upload", {
//       //     method: "POST",
//       //     headers: { "Content-Type": "multipart/form-data" },
//       //     body: stream,
//       //     allowHTTP1ForStreamingUpload: true,
//       //   })

//       //   console.log("Upload complete!")
//       // }
//     })
//     .catch((err) => console.error("Error: " + err));
// </script> -->


// <!-- <script type="module">


//   navigator.mediaDevices.getUserMedia({
//     audio: { channelCount: 1, sampleRate: { ideal: 16000 } },
//     video: false,
//   })
//     .then(spectrum).catch(console.log);

//   function spectrum(stream) {
//     const audioCtx = new AudioContext();

//     const randomNoiseNode = new AudioWorkletNode(audioCtx, 'random-noise-processor')
//     const analyser = audioCtx.createAnalyser();
//     const microphone = audioCtx.createMediaStreamSource(stream);
//     microphone.connect(analyser);

//     console.log({ microphone, analyser})
//     console.log({sr: audioCtx.sampleRate, cc: audioCtx.destination.channelCount})

//     const canvas = div.appendChild(document.createElement("canvas"));
//     canvas.width = window.innerWidth - 20;
//     canvas.height = window.innerHeight - 20;
//     const ctx = canvas.getContext("2d");
//     const data = new Uint8Array(canvas.width);
//     ctx.strokeStyle = 'rgb(0, 125, 0)';

//     setInterval(() => {
//       ctx.fillStyle = "#a0a0a0";
//       ctx.fillRect(0, 0, canvas.width, canvas.height);


//       analyser.getByteTimeDomainData(data);
//       ctx.lineWidth = 5;
//       ctx.beginPath();
//       x = 0;
//       for (let d of data) {
//         const y = canvas.height - (d / 128) * canvas.height / 2;
//         x ? ctx.lineTo(x++, y) : ctx.moveTo(x++, y);
//       }
//       ctx.stroke();
//     }, 1000 * canvas.width / audioCtx.sampleRate);
//   };

// </script> -->
