exports.command = function(timeout, callback){
  this.pause(250);
  this.expect.element('#kernel_indicator_icon').to.have.attribute("title").equals("Kernel Idle").before(timeout);

  this.assertKernelIdle();

  if (typeof callback === "function") { callback.call(self) }
  return this;
};
