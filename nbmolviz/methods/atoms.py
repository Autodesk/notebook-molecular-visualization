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
import ipywidgets as ipy


def draw2d(atom, **kwargs):
    """ Draw a 2D viewer with this atom highlighted (Jupyter only).
    In biomolecules, only draws the atom's residue.

    Args:
        width (int): width of viewer in pixels
        height (int): height of viewer in pixels

    Returns:
        mdt.ChemicalGraphViewer: viewer object
    """
    if atom.molecule:
        if atom.molecule.is_small_molecule:
            return atom.molecule.draw2d(highlight_atoms=[atom], **kwargs)
        else:
            return atom.residue.draw2d(highlight_atoms=[atom], **kwargs)
    else:
        raise ValueError("Cant draw an atom that's not part of a molecule.")


# @utils.args_from(mdt.molecule.Molecule.draw2d, allexcept=['highlight_atoms'])  # import order
def draw3d(atom, **kwargs):
    """ Draw a 3D viewer with this atom highlighted (Jupyter only).

    Args:
        width (int): width of viewer in pixels
        height (int): height of viewer in pixels

    Returns:
        mdt.GeometryViewer: viewer object
    """
    return atom.molecule.draw3d(highlight_atoms=[atom], **kwargs)


def draw(atom, width=300, height=300):
    """ Draw a 2D and 3D viewer with this atom highlighted (notebook only)

    Args:
        width (int): width of viewer in pixels
        height (int): height of viewer in pixels

    Returns:
        HBox: viewer object
    """
    viz2d = atom.draw2d(width=width, height=height, display=False)
    viz3d = atom.draw3d(width=width, height=height, display=False)
    return HBox([viz2d, viz3d])

