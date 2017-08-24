// TEMPLATE FROM https://github.com/jupyter/widget-cookiecutter

// This file contains the javascript that is run when the notebook is loaded.
// It contains some requirejs configuration and the `load_ipython_extension`
// which is required for any notebook extension.

// Configure requirejs
if (window.require) {
    window.require.config({
        map: {
            "*" : {
                "nbmolviz-js": "nbextensions/nbmolviz-js/index",
                "jupyter-js-widgets": "nbextensions/jupyter-js-widgets/extension"
            }
        }
    });
}

function loadJupyterExtension () {
    // Load CSS:
    $('<link/>')
        .appendTo('head')
        .attr({
            id: 'nbmolviz_css',
            rel: 'stylesheet',
            type: 'text/css',
            href: window.require.toUrl('nbextensions/nbmolviz-js/nbmolviz.css')
        });
}

// Export the required load_ipython_extension
module.exports = {
    load_ipython_extension: loadJupyterExtension
};
