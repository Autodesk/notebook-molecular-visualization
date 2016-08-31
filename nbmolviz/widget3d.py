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
import os
import traitlets
from ipywidgets import register

from nbmolviz.base_widget import MessageWidget

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)


class MolViz3DBaseWidget(MessageWidget):
    """
    This is our base class to communicate with an arbitrary JS backend
    """

    STYLE_SYNONYMS = {'vdw': 'vdw', 'sphere': 'vdw', 'cpk': 'vdw',
                      'licorice': 'licorice', 'stick': 'licorice', 'tube':'licorice',
                      'ball_and_stick': 'ball_and_stick',
                      'line': 'line',
                      'cartoon': 'ribbon', 'ribbon': 'ribbon',
                      None: None, 'hide': None, 'invisible': None, 'remove': None}

    def __init__(self, mol=None,
                 width=500, height=400,
                 **kwargs):
        super(MolViz3DBaseWidget, self).__init__(width=width, height=height,
                                                 **kwargs)
        # current state
        self.num_frames = 1
        self.current_frame = 0
        self.current_orbital = None

        #add the new molecule if necessary
        if mol is not None: self.add_molecule(mol)

    #some convenience synonyms
    def sphere(self, **kwargs):
        return self.add_style('vdw', **kwargs)
    vdw = cpk = sphere

    def ball_and_stick(self, **kwargs):
        return self.add_style('ball_and_stick', **kwargs)

    def licorice(self, **kwargs):
        return self.add_style('licorice', **kwargs)
    stick = tube = licorice

    def line(self, **kwargs):
        return self.add_style('line', **kwargs)

    def ribbon(self, **kwargs):
        return self.add_style('cartoon', **kwargs)
    cartoon = ribbon

    def hide(self, atoms=None):
        return self.add_style(None,atoms=atoms)
    invisible = hide

    #Abstract methods below
    def append_frame(self, positions=None, annotation=None):
        """
        :param positions: array in angstroms, otherwise just pulled from the molecule
        :param framenum: frame number to set (otherwise, append)
        :param annotation:
        :return: frame index
        """
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def add_molecule(self, molecule):
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def set_background_color(self, color, opacity):
        """
        :param color: a name or hex value
        :param opacity: a float between 0.0 and 1.0 inclusive
        :return:
        """
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def highlight_atoms(self,atoms):
        """
        Highlight these atoms
        """
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def set_style(self, style, atoms=None, color=None, radius=None, bondradius=None):
        """
        Sets an atom's style to be exactly this, removing any other representations
        :param style: choose from keys in STYLE_SYNONYMS
        :param atoms: iterable object with atoms in it
        :param color: EITHER A) color (name OR hex), B) a list of colors (same length as atoms), or color scheme object
        :param radius: EITHER A) a radius (in angstroms), or B) list of radii
        :param radius: EITHER A) a radius (in angstroms), or B) list of radii
        :param bondradius: width to draw radius in angstroms
        :return:
        """
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def add_style(self, style, atoms=None, color=None, radius=None, bondradius=None):
        """
        Adds this representation to an atom without removing any other representations
        :param style: choose from keys in STYLE_SYNONYMS
        :param atoms: iterable object with atoms in it
        :param color: EITHER A) color (name OR hex), B) a list of colors (same length as atoms), or color scheme object
        :param radius: EITHER A) a radius (in angstroms), or B) list of radii
        :param radius: EITHER A) a radius (in angstroms), or B) list of radii
        :param bondradius: width to draw radius in angstroms
        :return:
        """
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def draw_orbital(self, orbname, npts=50, isoval=0.01,
                     opacity=0.95, negative_color='red',
                     positive_color='blue'):
        self.current_orbital = orbname
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def draw_sphere(self,position_or_atom,radius=2.0,color='red',opacity=1.0):
        """
        Draw a sphere centered at passed atom or at the passed position
        :return: jsobject
        """
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def show_frame(self,framenum):
        raise NotImplementedError("This method must be implemented by the backend visualization class")

    def get_input_file(self):
        raise NotImplementedError("This method must be implemented by the interface class")

    def _atoms_to_json(self,atoms):
        raise NotImplementedError("This method must be implemented by the interface class")

    def calc_orb_grid(self,orbname):
        raise NotImplementedError("This method must be implemented by the interface class")

    def get_positions(self):
        raise NotImplementedError("This method must be implemented by the interface class")


