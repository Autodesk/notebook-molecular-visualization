/* A custom nightwatch functions loosely based on
https://github.com/hainm/nbtests
*/

const nbtokenstr = process.env.GALILEO_NBTOKEN ? `?token=${process.env.GALILEO_NBTOKEN}` : '';

exports.command = function (notebookName, callback) {
    const url = `${process.env.GALILEO_NBSERVER}/notebooks/${notebookName}${nbtokenstr}`;
    const result = this.url(url);
    this.waitForElementVisible('#notebook', 10000);
    this.pause(1000);  // extra 1 s of breathing time before proceeding ... necessary?
    this.waitForIdleKernel();
    if (typeof callback === "function") callback.call(this, result);
    return result;
};
