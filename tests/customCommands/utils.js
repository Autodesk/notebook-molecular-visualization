/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/
/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/

module.exports = {
    kernelWait: function (self, timeout) {
        let waitTime = 0;
        while (waitTime < timeout && Jupyter.notebook.kernel_busy) {
            self.pause(500);
            waitTime += 500;
        }
    }
};