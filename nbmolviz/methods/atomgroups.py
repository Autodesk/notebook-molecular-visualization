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

from IPython.display import display as dsp
import traitlets

from .. import viewers
from ..uielements.components import HBox
from ..widgets.components import AtomInspector


def draw(group, width=None, height=None, show_2dhydrogens=None, display=False,
         **kwargs):
    """ Visualize this molecule (Jupyter only).

    Creates a 3D viewer, and, for small molecules, a 2D viewer).

    Args:
        width (str or int): css width spec (if str) or width in pixels (if int)
        height (str or int): css height spec (if str) or height in pixels (if int)
        show_2dhydrogens (bool): whether to show the hydrogens in 2d (default: True if there
               are 10 or less heavy atoms, false otherwise)
        display (bool): immediately display this viewer
        **kwargs (dict): keyword arguments for GeometryViewer only

    Returns:
        moldesign.ui.SelectionGroup
    """

    atom_inspector = AtomInspector(group.atoms)

    if group.num_atoms < 40:
        width = width if width is not None else 500
        height = height if height is not None else 500
        viz2d = draw2d(group, width=width, height=height,
                       display=False,
                       show_hydrogens=show_2dhydrogens)
        viz3d = draw3d(group, width=width, height=height,
                       display=False, **kwargs)
        traitlets.link((viz3d, 'selected_atom_indices'), (viz2d, 'selected_atom_indices'))
        views = HBox([viz2d, viz3d])
    else:
        viz2d = None
        viz3d = draw3d(group, display=False, **kwargs)
        views = viz3d

    traitlets.link((viz3d, 'selected_atom_indices'),
                   (atom_inspector, 'selected_atom_indices'))

    if viz2d:
        traitlets.link((viz2d, 'selected_atom_indices'),
                       (atom_inspector, 'selected_atom_indices'))

    displayobj = viewers.ViewerContainer([views, atom_inspector],
                                         viewer=viz3d,
                                         graphviewer=viz2d)

    if display:
        dsp(displayobj)
    return displayobj


def draw3d(group, highlight_atoms=None, **kwargs):
    """ Draw this object in 3D. Jupyter only.

    Args:
        highlight_atoms (List[Atom]): atoms to highlight when the structure is drawn

    Returns:
        mdt.GeometryViewer: 3D viewer object
    """
    group.viz3d = viewers.GeometryViewer(group, **kwargs)
    if highlight_atoms is not None:
        group.viz3d.highlight_atoms(highlight_atoms)
    return group.viz3d


def draw2d(group, highlight_atoms=None, show_hydrogens=None, **kwargs):
    """
    Draw this object in 2D. Jupyter only.

    Args:
        highlight_atoms (List[Atom]): atoms to highlight when the structure is drawn
        show_hydrogens (bool): whether to draw the hydrogens or not (default: True if there
               are 10 or less heavy atoms, false otherwise)

    Returns:
        mdt.ChemicalGraphViewer: 2D viewer object
    """
    if show_hydrogens is None:
        show_hydrogens = len(group.heavy_atoms) <= 10
    if not show_hydrogens:
        alist = [atom for atom in group.atoms if atom.atnum > 1]
    else:
        alist = group
    group.viz2d = viewers.DistanceGraphViewer(alist, **kwargs)
    if highlight_atoms: group.viz2d.highlight_atoms(highlight_atoms)
    return group.viz2d
