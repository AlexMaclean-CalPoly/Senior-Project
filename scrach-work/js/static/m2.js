var constraints = { audio: true };
var chunks = [];

const audio = document.getElementById("au");
const button = document.getElementById("b1");

async function sendBlob(blob) {
  var oReq = new XMLHttpRequest();
  oReq.open("POST", "/a", true);
  oReq.send(blob);

  oReq.onload = function (oEvent) {
    console.log(oReq.responseText);
  };
}

navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
  var mediaRecorder = new MediaRecorder(stream);

  button.onclick = () => {
    console.log("stop");
    mediaRecorder.stop();
  };

  mediaRecorder.ondataavailable = (e) => {
    console.log(e);
    sendBlob(e.data);
    var blob = e.data;

    audio.controls = true;
    //var blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
    var audioURL = URL.createObjectURL(blob);
    audio.src = audioURL;
  };

  console.log("start");
  mediaRecorder.start();
});
