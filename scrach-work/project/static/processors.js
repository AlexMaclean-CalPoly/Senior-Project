
class StreamProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    var targetChunkLength = 0.16; // Approximate, in sec. Actual chunk may be smaller
    this.sampleRate = options.processorOptions.sampleRate;
    this.outputChunk = new Int16Array(this.sampleRate * targetChunkLength);
    this.offset = 0;
  }

  /*
   * Convert Float32Array from the AudioBuffer into Int16Array/PCM and add to the output buffer
   */
  floatTo16BitPCM(input) {
    // By the spec, this is probably 128 frames, but it can change

    // If we are about to overrun the output buffer, drop the remainder of the render quantum/input.
    // This should not happen in normal circumstances, since we aim to send the buffer before an overrun
    var end = Math.min(this.outputChunk.length - this.offset, input.length);
    for (let i = 0; i < end; i++) {
      let s = Math.max(-1, Math.min(1, input[i]));
      this.outputChunk[this.offset + i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }

    if (end < input.length) {
      console.log("WARNING: trimming end of render quantum");
    }
    this.offset = this.offset + end;
  }

  process(inputs, outputs, parameters) {
    // Use the first channel of the first input
    if (
      inputs == undefined ||
      inputs[0] == undefined ||
      inputs[0][0] == undefined
    ) {
      return true;
    }

    this.floatTo16BitPCM(inputs[0][0]);
    // when we get close to the end of the PCM buffer, send it
    if (this.outputChunk.length < this.offset + inputs[0][0].length) {
      this.port.postMessage(this.outputChunk.slice(0, this.offset));
      this.offset = 0;
    }

    return true;
  }
}

registerProcessor("stream-processor", StreamProcessor);
