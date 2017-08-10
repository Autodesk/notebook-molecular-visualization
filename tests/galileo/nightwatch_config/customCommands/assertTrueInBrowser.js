exports.command = function(fn, errmsg, callback){
  const self = this;
  function checkTrue(result){
    if(!result.value){throw Error('wtf');}
    self.assert.ok(result.value, errmsg)}
  this.execute(fn, [], checkTrue);
  if (typeof callback === "function") { callback.call(self) }
  return this;
};
