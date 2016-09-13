// based on https://github.com/bloomberg/bqplot/blob/master/js/src/index.js

// Entry point for the notebook bundle containing custom model definitions.
//
// Setup notebook base URL
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
__webpack_public_path__ = document.querySelector('body').getAttribute('data-base-url') +
    'nbextensions/nbmolviz-js/';

module.exports = {};

var exportAllFrom = [
    require("./molviz2d"),
    require("./molviz3d")
];

for (var i in exportAllFrom) {
    if (exportAllFrom.hasOwnProperty(i)) {
        var loadedModule = exportAllFrom[i];
        for (var target_name in loadedModule) {
            if (loadedModule.hasOwnProperty(target_name)) {
                module.exports[target_name] = loadedModule[target_name];
            }
        }
    }
}
module.exports['version'] = require('../package.json').version;
