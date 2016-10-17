import React from 'react';
import ReactMolecule2D from 'nbmolviz2d';
import widgets from 'jupyter-js-widgets';

class Nbmolviz2dComponent extends React.Component {
  constructor(props) {
    super(props);

    props.model.on('change', this.updateFromModel.bind(this));

    this.state = {
      width: 0,
      height: 0,
      modelData: {},
      selectedAtomIds: [],
    };
  }

  onChangeSelection(selectedAtomIds) {
    this.props.model.set('selected_atom_indices', selectedAtomIds);
  }

  updateFromModel(model = this.props.model) {
    this.setState({
      width: model.get('width'),
      height: model.get('height'),
      modelData: model.get('modelData'),
      selectedAtomIds: model.get('selectedAtomIds'),
    });
  }

  componenWillReceiveProps(nextProps) {
    this.updateFromModel(nextProps.model);
  }

  render() {
    return (
      <ReactMolecule2D
        width={this.state.width}
        height={this.state.height}
        modelData={this.state.modelData}
        selectedAtomIds={this.state.selectedAtomIds}
        onChangeSelection={this.onChangeSelection}
      />
    );
  }
}

Nbmolviz2dComponent.propTypes = {
  model: React.PropTypes.instanceOf(widgets.DOMWidgetModel),
};

export default Nbmolviz2dComponent;
