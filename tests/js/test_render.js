/**
 * Created by aaronvirshup on 7/18/17.
 */
module.exports = {
    "testSmallMoleculeRender": function (browser) {
        browser.openNotebook("notebooks/test_draw_small_molecule.ipynb");
        browser.restartKernel(2000);
        for ( var i = 0; i < 3; i++) {
           browser.executeCell(i)
                  .pause(3000)
                  .cellHasError(i)
                  .saveScreenshot('SmallMoleculeRender.png');
        }
        browser.end();
    },

}