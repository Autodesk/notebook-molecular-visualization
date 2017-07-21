/* Custom nightwatch functions based on
 https://github.com/hainm/nbtests
 */
const checkError = require("./utils").checkError;

exports.command = function(timeout, callback) {
  const self = this;

  this.waitForIdleKernel();
  this.perform(function(){process.stdout.write('Clear old output... ')});

  this.execute(
    function(){Jupyter.notebook.clear_output()}, [],
    checkError.bind(self));
  this.waitForIdleKernel();

  if (typeof callback === "function") { callback.call(self) }

  return this; // allows the command to be chained.
};
