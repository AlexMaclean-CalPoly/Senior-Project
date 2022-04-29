// This is "processor.js" file, evaluated in AudioWorkletGlobalScope upon
// audioWorklet.addModule() call in the main global scope.
registerProcessor(
  "my-worklet-processor",
  class extends AudioWorkletProcessor {
    constructor() {
      super();
      this._callback = null;
    }

    process(inputs, outputs, parameters) {
      // audio processing code here.
      const data = inputs[0][0];
      const blob = data.buffer;
      console.log({ blob, cb: this.callback });
      if (this.callback) {
        this.callback(blob);
      }
      return true;
    }
    get callback() {
      return this._callback;
    }

    set callback(value) {
      this._callback = value;
    }

    foo() {
      return 5;
    }
  }
);
