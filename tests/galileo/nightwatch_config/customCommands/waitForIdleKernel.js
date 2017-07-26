exports.command = function(timeout, assertIdle, callback){
  /* Block until Jupyter kernel is idle. Default timeout is 30000 ms if not specified. */

  if(arguments.length == 2 && typeof(assertIdle) == 'function'){
    callback = assertIdle;
    assertIdle = true;
  }

  if(timeout == undefined){
    timeout = 30000;
  }

  this.pause(250);
  // uses TWO different methods to check, since apparently neither is reliable on its own

  // method 1: wait for UI element
  this.expect.element('#kernel_indicator_icon').to.have.attribute("title").equals("Kernel Idle").before(timeout);

  // method 2: wait for Jupyter API
  this.waitForTrue(function(){return !Jupyter.notebook.kernel_busy}, timeout);

  if(assertIdle) this.assertKernelIdle();

  if (typeof callback === "function") { callback.call(self) }
  return this;
};
