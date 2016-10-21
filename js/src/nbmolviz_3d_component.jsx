import React from 'react';
import Molecule3d from 'molecule-3d-for-react';
import widgets from 'jupyter-js-widgets';

class Nbmolviz3dComponent extends React.Component {
  static getStateFromModel(model) {
    return {
      width: model.get('width'),
      height: model.get('height'),
      modelData: model.get('model_data'),
      selectedAtomIds: model.get('selected_atom_indices'),
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
        width={this.state.width}
        height={this.state.height}
        modelData={this.state.modelData}
        selectedAtomIds={this.state.selectedAtomIds}
        onChangeSelection={this.onChangeSelection}
      />
    );
  }
}

Nbmolviz3dComponent.propTypes = {
  model: React.PropTypes.instanceOf(widgets.DOMWidgetModel),
};

export default Nbmolviz3dComponent;
