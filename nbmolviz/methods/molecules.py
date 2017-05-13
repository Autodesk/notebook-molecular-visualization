# Copyright 2016 Autodesk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def draw_orbitals(mol, **kwargs):
    """ Visualize any calculated molecular orbitals (Jupyter only).

    Returns:
        mdt.orbitals.OrbitalViewer
    """
    from ..widgets.orbitals import OrbitalViewer

    if 'wfn' not in mol.properties:
        mol.calculate_wfn()
    return OrbitalViewer(mol, **kwargs)


def configure_methods(mol):
    """ Interactively configure this molecule's simulation methods (notebooks only)

    Returns:
        ipywidgets.Box: configuration widget
    """
    import ipywidgets as ipy

    children = []
    if mol.energy_model:
        children.append(mol.energy_model.configure())

    if mol.integrator:
        children.append(mol.integrator.configure())

    return ipy.VBox(children)


def markdown_summary(mol):
    """A markdown description of this molecule.

    Returns:
        str: Markdown"""
    # TODO: remove leading underscores for descriptor-protected attributes
    lines = ['### Molecule: "%s" (%d atoms)'%(mol.name, mol.natoms)]

    description = mol.metadata.get('description', None)
    if description is not None:
        description = mol.metadata.description[:5000]
        url = mol.metadata.get('url', None)
        if url is not None:
            description = '<a href="%s" target="_blank">%s</a>' % \
                          (url, description)
        lines.append(description)

    lines.extend([
             '**Mass**: {:.2f}'.format(mol.mass),
             '**Formula**: %s'%mol.get_stoichiometry(html=True),
             '**Charge**: %s'%mol.charge])

    if mol.energy_model:
        lines.append('**Potential model**: %s'%str(mol.energy_model))

    if mol.integrator:
        lines.append('**Integrator**: %s'%str(mol.integrator))

    if mol.is_biomolecule:
        lines.extend(mol.biomol_summary_markdown())

    return '\n\n'.join(lines)
