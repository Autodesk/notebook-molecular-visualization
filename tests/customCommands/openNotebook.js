/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/

exports.command = function (notebookName, callback) {
    let result = this.url("http://localhost:5678/notebooks/" + notebookName);
    this.waitForElementVisible('#notebook', 10000);
    this.pause(1000);  // extra 1 s of breathing time before proceeding ... necessary?
    this.waitForIdleKernel();
    if (typeof callback === "function") callback.call(this, result);
    return result;
};
