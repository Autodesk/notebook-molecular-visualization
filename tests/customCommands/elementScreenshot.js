/*
Slightly adapted from code by @petrogad on github
See https://github.com/nightwatchjs/nightwatch/issues/547#issuecomment-118975377
 */

const png = require('png-crop');

exports.command = { function(browser, selector) {
    browser.element('css selector', selector, function(element) {
      browser.elementIdLocationInView(element.value.ELEMENT, function(location) {
        browser.elementIdSize(element.value.ELEMENT, function(size) {
          browser.saveScreenshot('screenshots/test.png', function() {
            let config = {
              width: size.value.width*2, //needed 2x due to monitor resolution
              height: size.value.height*2, //needed 2x due to monitor resolution
              top: location.value.y*2, //needed 2x due to monitor resolution
              left: location.value.x*2 //needed 2x due to monitor resolution
            };

            png.crop(
              'screenshots/test.png',
              'screenshots/test_cropped.png',
              config,
              function(err) {
                console.log(err);
              }
            );
          });
        });
      });
    })
  }
};