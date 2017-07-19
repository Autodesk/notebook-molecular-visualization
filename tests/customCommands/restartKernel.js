/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
 */

import kernelWait from './utils'


exports.command = function(timeout, callback) {
    const self = this;

    this.execute(
        function() {
            Jupyter.notebook.kernel.restart();
        },
        null, // arguments array to be passed
        function(result) {
            self.pause(timeout);
            if (typeof callback === "function") {
                callback.call(self, result);
            }
        }
    );

    return this; // allows the command to be chained.
};