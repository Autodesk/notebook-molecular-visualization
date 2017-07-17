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
import Molecule2D from 'molecule-2d-for-react';
import widgets from 'jupyter-js-widgets';

class Nbmolviz2dComponent extends React.Component {
  static getStateFromModel(model) {
    const links = model.get('graph').links.map((link, index) =>
      Object.assign({}, link, { id: typeof link.id === 'number' ? link.id : index })
    );
    const nodes = model.get('graph').nodes.map(node =>
      Object.assign({}, node, { id: typeof node.id === 'number' ? node.id : node.index })
    );

    return {
      width: model.get('width'),
      height: model.get('height'),
      modelData: {
        nodes,
        links,
      },
      selectedAtomIds: model.get('selected_atom_indices'),
    };
  }

  constructor(props) {
    super(props);

    props.model.on('change', () => {
      this.setState(Nbmolviz2dComponent.getStateFromModel(this.props.model));
    });

    this.onChangeSelection = this.onChangeSelection.bind(this);

    this.state = Nbmolviz2dComponent.getStateFromModel(props.model);
  }

  onChangeSelection(selectedAtomIds) {
    this.props.model.set('selected_atom_indices', selectedAtomIds);
    this.props.model.save();
  }

  componenWillReceiveProps(nextProps) {
    this.setState(Nbmolviz2dComponent.getStateFromModel(nextProps.model));
  }

  render() {
    return (
      <div>
        <Molecule2D
          width={this.state.width}
          height={this.state.height}
          modelData={this.state.modelData}
          selectedAtomIds={this.state.selectedAtomIds}
          onChangeSelection={this.onChangeSelection}
        />
      </div>
    );
  }
}

Nbmolviz2dComponent.propTypes = {
  model: React.PropTypes.instanceOf(widgets.DOMWidgetModel),
};

export default Nbmolviz2dComponent;
