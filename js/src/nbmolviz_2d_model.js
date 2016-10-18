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

const Nbmolviz2dModel = widgets.DOMWidgetModel.extend({
  defaults: {
    _model_name: 'MolWidget2DModel',
    _view_name: 'MolWidget2DView',
    _model_module: 'nbmolviz-js',
    _view_module: 'nbmolviz-js',
    charge: 0.0,
    uuid: '',
    graph: {
      nodes: [
        { atom: 'H', category: 'dodgerblue', index: 0, id: 0 },
        { atom: 'H', category: 'dodgerblue', index: 1, id: 1 },
        { atom: 'O', category: 'tomato', index: 2, id: 2 },
      ],
      links: [
        { source: 0, target: 2, bond: 1, category: 0 },
        { source: 1, target: 2, bond: 1, category: 0 },
      ],
    },
    selected_atom_indices: [],
    clicked_bond_indices: {},
    _atom_colors: {},
    width: 500.0,
    height: 500.0,
  },
});

export default Nbmolviz2dModel;
