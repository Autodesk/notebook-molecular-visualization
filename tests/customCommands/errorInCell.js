/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/


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
                if (result.value.output_type == 'error') {
                    console.log('error code', result.value.code);
                }
                self.verify.ok(result.value.output_type != 'error', "Check that python has no error");
            }   }

        if (typeof callback === "function") {
            callback.call(self, result);
        }
    }

    this.execute(checkCell, [cellNumber], verify);

    return this; // allows the command to be chained.
};