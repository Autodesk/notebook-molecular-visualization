/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/

const kernelWait = require("./utils").kernelWait;
checkError = require("./utils").checkError;


exports.command = function (cellNumber, timeout, callback) {
    /* Synchronously run cell `cellNumber` in the active notebook.  Default timeout 60 s*/

    if (arguments.length == 1){ timeout = 60000 }

    function cellRunner(cellNumber){
        /* Asynchronously run cell `cellNumber` in the active notebook. */
        const cell = Jupyter.notebook.get_cell(cellNumber);
        Jupyter.notebook.scroll_to_cell(cellNumber);
        if (cell) { cell.execute() }
    }

    console.log('Executing cell ' + cellNumber);
    this.execute(cellRunner, [cellNumber], checkError.bind(this))
      .waitForIdleKernel(timeout)
      .execute(function(cellNumber){Jupyter.notebook.scroll_to_cell(cellNumber)},
        [cellNumber], checkError.bind(this));


    if (typeof callback === "function") { callback.call(this) };
    return this; // allows the command to be chained.
};
