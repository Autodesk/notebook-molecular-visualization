/* Custom nightwatch functions based on
https://github.com/hainm/nbtests
*/


module.exports = {
    kernelWait: function (browser, timeout) {
        let waitTime = 0;
        while (waitTime < timeout && kernelIsBusy(browser)) {
            browser.pause(500);
            waitTime += 500;
        }
        console.log('Kernel ready after ' + waitTime + ' ms.');
        browser.pause(500);
    },

    checkError: function(result){
        /* Checks that `client.execute` completed succesfully. Must be bound to client as `this` */
        this.assert.ok(result.status == 0, result)
    }
};