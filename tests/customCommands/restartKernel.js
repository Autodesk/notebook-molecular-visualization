/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
 */
const checkError = require("./utils").checkError;

exports.command = function(timeout, callback) {
  const self = this;

  this.execute(
    function(){Jupyter.notebook.restart_clear_output({"confirm":false})}, [],
    checkError.bind(self));

  this.expect.element('#notification_kernel').to.be.visible.before(250);
  this.expect.element('#notification_kernel').to.not.be.visible.before(timeout);

  if (typeof callback === "function") { callback.call(self) }

  return this; // allows the command to be chained.
};