/**
 * Copyright 2016 Autodesk Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import widgets from 'jupyter-js-widgets';
import {
  Nbmolviz2dModel,
  Nbmolviz2dView,
} from 'nbmolviz2d';
import widgetUtils from './utils/widget_utils';

let molModelPrototype = Object.assign({}, Nbmolviz2dModel.prototype);
delete molModelPrototype.constructor;

const MolWidget2DModel = widgets.DOMWidgetModel.extend(
  Object.assign({}, molModelPrototype)
);

// Call both initialize functions for model and view below
const molViewPrototype = Object.assign({}, Nbmolviz2dView.prototype);
molViewPrototype.initialize = widgetUtils.getMultiFunction(
  molViewPrototype.initialize,
  widgets.DOMWidgetView.prototype.initialize
);

const MolWidget2DView = widgets.DOMWidgetView.extend(
  Object.assign({}, molViewPrototype)
);

module.exports = {
  MolWidget2DModel : MolWidget2DModel,
  MolWidget2DView : MolWidget2DView,
};
