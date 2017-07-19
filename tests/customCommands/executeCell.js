/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/

import kernelWait from './utils';


exports.command = function (cellNumber, callback) {
    const self = this;

    function cellRunner(cellNumber){
        let cell = Jupyter.notebook.get_cell(cellNumber);
        if (cell) { cell.execute() }
        kernelWait(self, 10000);
    }
    function finish(result){
        this.verify.ok(!Jupyter.notebook.kernel_busy, 'Timed out waiting for Kernel to idle')
        if (typeof callback === "function") { callback.call(self, result) };
    }

    this.execute( cellRunner, [cellNumber], finish );
    return this; // allows the command to be chained.
};
