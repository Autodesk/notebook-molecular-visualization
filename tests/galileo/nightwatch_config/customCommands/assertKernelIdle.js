exports.command = function(callback){
  this.assertTrueInBrowser(
    function(){return !Jupyter.notebook.kernel_busy},
    "Kernel was busy but was expected to be idle.");

  if (typeof callback === "function") { callback.call(self) }
  return this;
};
