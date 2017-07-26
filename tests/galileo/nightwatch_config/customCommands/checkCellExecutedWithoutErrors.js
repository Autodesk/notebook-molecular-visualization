/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/


// in case of Python errors, output is in a div INSIDE of outputarea div, with classes:
// "output_subarea output_text output_error"
// Can also get from Jupyter API directly by checking for an output area s.t.
// Jupyter.notebook.get_cell(cellNum).output_area.outputs[i].output_type == 'error'

exports.command = function(cellNumber, callback) {
    const self = this;

    function checkCell(cellNumber){
        let cell = Jupyter.notebook.get_cell(cellNumber);

        if (cell.output_area.outputs.length > 0) {
            let out = cell.output_area.outputs[0];
            return {output_type: out.output_type, code: cell.input[0].innerText};
        }else {
            return {output_type: 'blank', code: cell.input[0].innerText};
        }    }

    function verify(result){
        if (result.value != null) {
            if (result.value.output_type) {
                let error = 'not found';
                if (result.value.output_type == 'error') {
                    console.log('error code', result.value.code);
                    error = result.value
                }
                self.verify.ok(result.value.output_type != 'error',
                    "Error executing cell " + cellNumber + ': \n' + error);
            }   }

        if (typeof callback === "function") {
            callback.call(self, result);
        }
    }

    this.execute(checkCell, [cellNumber], verify);

    return this; // allows the command to be chained.
};