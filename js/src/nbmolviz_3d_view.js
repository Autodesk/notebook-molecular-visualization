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
import React from 'react';
import { render } from 'react-dom';
import ReactMolecule3D from 'nbmolviz3d';
import widgets from 'jupyter-js-widgets';

const Nbmolviz3dView = widgets.DOMWidgetView.extend({

  tagName: 'div',

  initialize() {
    this.model.on('change', this.render.bind(this));
  },

  onChangeSelection(selectedAtomIds) {
    this.model.set('selected_atom_indices', selectedAtomIds);
  },

  render() {
    this.el.innerHTML = '';
    render(React.createElement(ReactMolecule3D, {
      width: this.model.get('width'),
      height: this.model.get('height'),
      modelData: this.model.get('model_data'),
      selectedAtomIds: this.model.get('selected_atom_indices'),
      onChangeSelection: this.onChangeSelection,
    }), this.el);
  },
});

export default Nbmolviz3dView;
