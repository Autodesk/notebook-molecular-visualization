/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/

const kernelWait = require("./utils").kernelWait;
checkError = require("./utils").checkError;


// xpath to get output area div (not tested):
/* `//*[@id="notebook-container"]/div[${cellNumber+1}]` + /div[@class="output_wrapper"]'+
'/div[@class="output"]' */

exports.command = function (cellNumber, timeout, callback) {
    /* Synchronously run cell `cellNumber` in the active notebook.  Default timeout is 60000 ms*/

    if (arguments.length == 1){ timeout = 60000 }

    function cellRunner(cellNumber){
        /* Asynchronously run cell `cellNumber` in the active notebook. */
        const cell = Jupyter.notebook.get_cell(cellNumber);
        Jupyter.notebook.scroll_to_cell(cellNumber);
        if (cell) { cell.execute() }
    }

    function cellDone(cellNumber){
      const cell = Jupyter.notebook.get_cell(cellNumber);
      return Number.isInteger(cell.input_prompt_number);
    }

  this.perform(function(){process.stdout.write('run cell ' + cellNumber + '... ')})
    .execute(cellRunner, [cellNumber], checkError.bind(this));


  this.waitForTrue(cellDone, 60000, [cellNumber])
    .waitForIdleKernel(timeout) //one more check to make ABSOLUTELY SURE it's done before moving on
    .execute(function(cellNumber){Jupyter.notebook.scroll_to_cell(cellNumber)},
      [cellNumber], checkError.bind(this));


    if (typeof callback === "function") { callback.call(this) };
    return this; // allows the command to be chained.
};
