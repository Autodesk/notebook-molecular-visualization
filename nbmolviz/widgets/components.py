from __future__ import print_function, absolute_import, division
from future.builtins import *
from future import standard_library
standard_library.install_aliases()
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
import traitlets
from moldesign import utils

from .. import viewers
from ..widget_utils import process_widget_kwargs
from ..uielements.components import HBox, VBox


class AtomInspector(ipy.HTML):
    """ Turn atom indices into a value to display

    To use this with a display widget, link its ``selected_atom_indices`` attribute to the
    display widget's list of selected atom indices.
    """
    selected_atom_indices = traitlets.List([])

    def __init__(self, atoms, **kwargs):
        super().__init__(**kwargs)
        self.atoms = atoms

    @traitlets.observe('selected_atom_indices')
    def atoms_to_value(self, change):
        atoms = [self.atoms[idx] for idx in change['new']]

        if len(atoms) == 0:
            return 'No selection'
        elif len(atoms) == 1:
            atom = atoms[0]
            res = atom.residue
            chain = res.chain
            lines = ["<b>Molecule</b>: %s<br>" % atom.molecule.name]
            if atom.chain.name is not None:
                lines.append("<b>Chain</b> %s<br>" % chain.name)
            if atom.residue.type != 'placeholder':
                lines.append("<b>Residue</b> %s, index %d<br>" % (res.name, res.index))
            lines.append("<b>Atom</b> %s (%s), index %d<br>" % (atom.name, atom.symbol, atom.index))
            self.value = '\n'.join(lines)

        elif len(atoms) > 1:
            atstrings = ['<b>%s</b>, index %s / res <b>%s</b>, index %s / chain <b>%s</b>' %
                         (a.name, a.index, a.residue.resname, a.residue.index, a.chain.name)
                         for a in atoms]
            self.value = '<br>'.join(atstrings)


class ViewerToolBase(ipy.Box):
    """
    The base for most viewer-based widgets - it consists of a viewer in the top-left,
    UI controls on the right, and some additional widgets underneath the viewer
    """
    VIEWERTYPE = viewers.GeometryViewer
    VIEWERWIDTH = '600px'

    selected_atom_indices = utils.Alias('viewer.selected_atom_indices')
    selected_atoms = utils.Alias('viewer.selected_atoms')

    def __init__(self, mol):
        self.mol = mol

        self.toolpane = VBox()
        self.viewer = self.VIEWERTYPE(mol, width=self.VIEWERWIDTH)

        self.subtools = ipy.Box()
        self.viewer_pane = VBox([self.viewer, self.subtools])
        self.main_pane = HBox([self.viewer_pane, self.toolpane])

        super().__init__([self.main_pane])

    def __getattr__(self, item):
        if hasattr(self.viewer, item):
            return getattr(self.viewer, item)
        else:
            raise AttributeError(item)


class ReadoutFloatSlider(VBox):
    description = traitlets.Unicode()
    value = traitlets.Float()

    def __init__(self, format=None, *args, **kwargs):
        description = kwargs.pop('description', 'FloatSlider')
        min = kwargs.setdefault('min', 0.0)
        max = kwargs.setdefault('max', 10.0)
        self.formatstring = format
        self.header = ipy.HTML()
        self.readout = ipy.Text(layout=ipy.Layout(width='100px'))
        self.readout.on_submit(self.parse_value)

        kwargs.setdefault('readout', False)
        self.slider = ipy.FloatSlider(*args, **process_widget_kwargs(kwargs))
        self.minlabel = ipy.HTML(u'<font size=1.5>{}</font>'.format(self.formatstring.format(min)))
        self.maxlabel = ipy.HTML(u'<font size=1.5>{}</font>'.format(self.formatstring.format(max)))
        self.sliderbox = HBox([self.minlabel, self.slider, self.maxlabel])
        traitlets.link((self, 'description'), (self.header, 'value'))
        traitlets.link((self, 'value'), (self.slider, 'value'))
        self.description = description
        self.update_readout()
        super().__init__([self.header,
                                                  self.readout,
                                                  self.sliderbox])

    @traitlets.observe('value')
    def update_readout(self, *args):
        self.readout.value = self.formatstring.format(self.value)

    def disable(self):
        self.slider.disabled = True
        self.readout.disabled = True

    def enable(self):
        self.slider.disabled = False
        self.readout.disabled = False

    def parse_value(self, *args):
        try:
            f = float(self.readout.value)
        except ValueError:
            s = self.readout.value
            match = utils.GETFLOAT.search(s)
            if match is None:
                self.readout.value = self.formatstring.format(self.slider.value)
                print("Couldn't parse string %s" % s)
                return
            else:
                f = float(s[match.start():match.end()])
        self.slider.value = f

