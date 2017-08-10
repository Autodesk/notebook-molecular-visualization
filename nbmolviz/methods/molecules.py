# Copyright 2017 Autodesk Inc.
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

from ..uielements.components import VBox


def draw_orbitals(mol, **kwargs):
    """ Visualize any calculated molecular orbitals (Jupyter only).

    Returns:
        mdt.orbitals.OrbitalViewer
    """
    from ..viewers.orbital_viewer import OrbitalViewer

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

    return VBox(children)

