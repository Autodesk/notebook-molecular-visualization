/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/

const nbport = process.env.GALILEO_NBPORT == undefined ? 8888 : process.env.GALILEO_NBPORT;
const nbtokenstr = process.env.GALILEO_NBTOKEN ? `?token=${process.env.GALILEO_NBTOKEN}` : '';

exports.command = function (notebookName, callback) {
    let result = this.url(`http://localhost:${nbport}/notebooks/${notebookName}${nbtokenstr}`);
    this.waitForElementVisible('#notebook', 10000);
    this.pause(1000);  // extra 1 s of breathing time before proceeding ... necessary?
    this.waitForIdleKernel();
    if (typeof callback === "function") callback.call(this, result);
    return result;
};
