/**
 * Copyright 2017 Autodesk Inc.
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
import Molecule3d from 'molecule-3d-for-react';
import widgets from 'jupyter-js-widgets';
import assert from 'assert';


class Nbmolviz3dComponent extends React.Component {
  static getStateFromModel(model) {
    const oldModelData = model.get('model_data');
    const positions = model.get('positions');
    const modelData = JSON.parse(JSON.stringify(oldModelData));

    if (modelData.hasOwnProperty('atoms')) {
        assert(modelData.atoms.length == positions.length);
        for (let i = 0; i < modelData.atoms.length; i++) {
            modelData.atoms[i].positions = positions[i];
        }
    }

    const orbital = JSON.parse(JSON.stringify(model.get('volumetric_style')));
    orbital.cube_file = model.get('cubefile');

    return {
      atomLabelsShown: model.get('atom_labels_shown'),
      backgroundColor: model.get('background_color'),
      backgroundOpacity: model.get('background_opacity'),
      farClip: model.get('far_clip'),
      height: model.get('height'),
      labels: model.get('labels'),
      modelData: modelData,
      nearClip: model.get('near_clip'),
      orbital: orbital,
      outlineColor: model.get('outline_color'),
      outlineWidth: model.get('outline_width'),
      selectedAtomIds: model.get('selected_atom_indices'),
      selectionType: model.get('selection_type'),
      shapes: model.get('shapes'),
      styles: model.get('styles'),
      width: model.get('width'),
    };
  }

  constructor(props) {
    super(props);

    this.onChangeSelection = this.onChangeSelection.bind(this);

    props.model.on('change', () => {
      this.setState(Nbmolviz3dComponent.getStateFromModel(this.props.model));
    });

    this.state = Nbmolviz3dComponent.getStateFromModel(props.model);
  }

  onChangeSelection(selectedAtomIds) {
    this.props.model.set('selected_atom_indices', selectedAtomIds);
    this.props.model.save();
  }

  componenWillReceiveProps(nextProps) {
    this.setState(Nbmolviz3dComponent.getStateFromModel(nextProps.model));
  }

  render() {
    return (
      <Molecule3d
        {...this.state}
        onChangeSelection={this.onChangeSelection}
      />
    );
  }
}

Nbmolviz3dComponent.propTypes = {
  model: React.PropTypes.instanceOf(widgets.DOMWidgetModel),
};

export default Nbmolviz3dComponent;
