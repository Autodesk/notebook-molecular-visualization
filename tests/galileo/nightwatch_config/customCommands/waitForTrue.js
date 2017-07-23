exports.command = function(testFunction, timeout, args){
  /* Wait for `testFunction` to return `true` when executed in the browser */

  if(arguments.length == 2) args = [];

  const self = this;
  let waitTime = 0.0;

  function checkResult(result){
    if(result.value) return;
    self.assert.ok(waitTime <= timeout, 'Timed out waiting for ' + testFunction);
    self.pause(1000);
    waitTime += 1000;
    self.execute(testFunction, args, checkResult);
  }

  self.execute(testFunction, args, checkResult);
  return this;
};
