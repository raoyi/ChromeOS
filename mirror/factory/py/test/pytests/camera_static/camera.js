// Copyright 2017 The Chromium OS Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

const VIDEO_START_PLAY_TIMEOUT_MS = 5000;
const imageDiv = document.getElementById('test-image');
const promptDiv = document.getElementById('prompt');

const showImage = (data_url) => {
  imageDiv.src = data_url;
};

const hideImage = (hide) => {
  imageDiv.classList.toggle('hidden', hide);
};

const getErrorMessage = (error) => `${error.name}: ${error.message}`;

// TODO(pihsun): Move this to util.js
const runJSPromise = (js, eventName) => {
  eval(js).then((data) => {
    test.sendTestEvent(eventName, {data});
  }).catch((error) => {
    test.sendTestEvent(eventName, {error: getErrorMessage(error)});
  });
};

const runJS = (js, eventName) => {
  try {
    const data = eval(js);
    test.sendTestEvent(eventName, {data});
  } catch (error) {
    test.sendTestEvent(eventName, {error: getErrorMessage(error)});
  }
};

const showInstruction = (instruction) => {
  goog.dom.safe.setInnerHtml(
      promptDiv, cros.factory.i18n.i18nLabel(instruction));
};

const canvasToDataURL = async (canvas) => {
  const blob = await canvas.convertToBlob({type: 'image/jpeg'});
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.readAsDataURL(blob);
  });
};

class CameraTest {
  constructor(options) {
    this.facingMode = options.facingMode;
    this.width = options.width;
    this.height = options.height;
    this.flipImage = options.flipImage;
    this.videoStream = null;
    // The width/height would be set to the true width/height in grabFrame.
    this.canvas = new OffscreenCanvas(this.width, this.height);
    this.videoElem = document.createElement('video');
    this.videoElemReadyForStreamCallback = null;

    this.videoElem.addEventListener('play', () => {
      if (this.videoElemReadyForStreamCallback !== null) {
        this.videoElemReadyForStreamCallback();
        this.videoElemReadyForStreamCallback = null;
      }
    });
    this.videoElem.autoplay = true;
  }

  async enable() {
    this.videoStream = await this.getVideoStreamTrack();
  }

  disable() {
    if (this.videoStream) {
      this.videoStream.stop();
      this.videoStream = null;
    }
  }

  async getVideoStreamTrack() {
    const mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        width: this.width,
        height: this.height,
        facingMode: {exact: this.facingMode}
      }
    });
    this.videoElem.srcObject = mediaStream;

    // Try to wait until |videoElem| starts to play so that |grabFrame|
    // can capture the data from it.
    // We expect the pytest invokes the API properly, this method shouldn't
    // be called before the previous call finishes.
    console.assert(this.videoElemReadyForStreamCallback === null);
    await new window.Promise((resolve, reject) => {
      // Fails if the |play| event is not raised in time.
      const timeoutId = window.setTimeout(() => {
        if (this.videoElemReadyForStreamCallback !== null) {
          this.videoElemReadyForStreamCallback = null;
          reject(new Error('timeout from video element'));
        }
      }, VIDEO_START_PLAY_TIMEOUT_MS);
      this.videoElemReadyForStreamCallback = () => {
        window.clearTimeout(timeoutId);
        resolve();
      };
    });

    return mediaStream.getVideoTracks()[0];
  }

  async grabFrame() {
    // Sometimes when the system is buzy, the videoStream become muted.
    // Restarting the stream solves the issue.
    if (this.videoStream.muted) {
      this.disable();
      await this.enable();
    }
    this.canvas.width = this.videoElem.videoWidth;
    this.canvas.height = this.videoElem.videoHeight;
    this.canvas.getContext('2d').drawImage(this.videoElem, 0, 0);
  }

  async grabFrameAndTransmitBack() {
    await this.grabFrame();
    const blobBase64 = (await canvasToDataURL(this.canvas))
                           .replace(/^data:image\/jpeg;base64,/, '');
    const goofy = test.invocation.goofy;
    const path = await goofy.sendRpc('UploadTemporaryFile', blobBase64);
    return path;
  }

  async detectFaces() {
    const faceDetector = new FaceDetector({maxDetectedFaces: 1});
    const faces = await faceDetector.detect(this.canvas);
    if (!faces.length) {
      return false;
    }
    const ctx = this.canvas.getContext('2d');
    ctx.lineWidth = 4;
    ctx.strokeStyle = 'white';
    for (let face of faces) {
      ctx.rect(face.x, face.y, face.width, face.height);
      ctx.stroke();
    }
    return true;
  }

  async scanQRCode() {
    const barcodeDetector = new BarcodeDetector({formats: ['qr_code']});
    const codes = await barcodeDetector.detect(this.canvas);
    if (!codes.length) {
      return null;
    }
    return codes[0].rawValue;
  }

  async showImage(ratio) {
    const {width, height} = this.canvas;
    const newWidth = Math.round(width * ratio);
    const newHeight = Math.round(height * ratio);
    const tempCanvas = new OffscreenCanvas(newWidth, newHeight);
    const ctx = tempCanvas.getContext('2d');
    if (this.flipImage) {
      // We flip the image horizontally so the image looks like a mirror.
      ctx.scale(-1, 1);
      ctx.drawImage(
          this.canvas, 0, 0, width, height, -newWidth, 0, newWidth, newHeight);
    } else {
      ctx.drawImage(
          this.canvas, 0, 0, width, height, 0, 0, newWidth, newHeight);
    }
    showImage(await canvasToDataURL(tempCanvas));
  }
}

const exports = {
  showImage,
  hideImage,
  runJSPromise,
  runJS,
  showInstruction,
  CameraTest
};
for (const key of Object.keys(exports)) {
  window[key] = exports[key];
}
