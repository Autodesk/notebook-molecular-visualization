/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/


// in case of Python errors, output is in a div INSIDE of outputarea div, with classes:
// "output_subarea output_text output_error"
// Can also get from Jupyter API directly by checking for an output area s.t.
// Jupyter.notebook.get_cell(cellNum).output_area.outputs[i].output_type == 'error'

exports.command = function(cellNumber, callback) {
  const self = this;

  function getError(cellNumber) {
    let cell = Jupyter.notebook.get_cell(cellNumber);
    let err = null;

    cell.output_area.outputs.forEach(function(oput){
      err = oput.evalue;
    });
    return err;
  }

  function verify(result){
    self.assert.ok(result.value == null,
      "Error executing cell " + cellNumber + ': ' + result.value);

    if (typeof callback === "function") {
      callback.call(self, result);
    }
  }

  this.execute(getError, [cellNumber], verify);

  return this; // allows the command to be chained.
};
