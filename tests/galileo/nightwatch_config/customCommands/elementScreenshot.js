const fs = require('fs-extra');
const gm = require('gm');
const path = require('path');
const loadImage = gm.subClass({imageMagick: true});
const checkError = require('./utils').checkError;

function getClientBoundingBox(selector) {
  return [document.querySelector(selector).getBoundingClientRect(),
          window.devicePixelRatio];
}

exports.command = function(selector, imagePath){
  const self = this;
  let bbox = null;
  let pixelRatio = null;

  function boundingBoxCallback(result) {
    self.perform(function() {
      checkError.bind(self)(result);
      bbox = result.value[0];
      pixelRatio = result.value[1];
    });
  }

  function cropAndSaveScreenshot(result){
    const latestPath = path.join(self.options.screenshotsPath, imagePath + '.png');
    process.stdout.write('Screenshot saved: ' + latestPath + '\n');

    fs.outputFileSync(latestPath, new Buffer(result.value, 'base64'));
    const shot = loadImage(latestPath).quality(100);
    shot.crop(
      bbox.width * pixelRatio,
      bbox.height * pixelRatio,
      bbox.left * pixelRatio,
      bbox.top * pixelRatio);
    shot.write(latestPath, err => {
      if (err) throw err;
    });
  }

  this.execute(getClientBoundingBox, [selector], boundingBoxCallback);
  this.screenshot(true, cropAndSaveScreenshot);
};