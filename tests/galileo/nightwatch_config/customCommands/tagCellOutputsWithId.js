const checkError = require("./utils").checkError;

exports.command = function(cellNum, tagName, callback){

  function tagCellOutputDivs(cellNum, tagName){
    let cell = Jupyter.notebook.get_cell(cellNum);
    cell.widgetarea.widget_area.id = tagName + "_widgetarea";
    cell.output_area.element[0].id = tagName + "_outputarea";
  }

  this.execute(
    tagCellOutputDivs,
    [cellNum, tagName],
    checkError.bind(this));

  if (typeof callback === "function") { callback.call(self) }
  return this; // allows the command to be chained.
};