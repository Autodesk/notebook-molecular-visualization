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
import uuid

import traitlets
from traitlets import Unicode
from nbmolviz.base_widget import MessageWidget
from nbmolviz.utils import translate_color


class MolViz2DBaseWidget(MessageWidget):
    """
    This is actually the D3.js graphics driver for the 2D base widget.
    It should be refactored with an abstract base class if
    there's a chance of adding another graphics driver.
    """
    _view_name = Unicode('MolWidget2DView').tag(sync=True)
    _model_name = Unicode('MolWidget2DModel').tag(sync=True)
    _view_module = Unicode('nbmolviz-js').tag(sync=True)
    _model_module = Unicode('nbmolviz-js').tag(sync=True)

    charge = traitlets.Float().tag(sync=True)
    uuid = traitlets.Unicode().tag(sync=True)
    graph = traitlets.Dict().tag(sync=True)
    clicked_atom_index = traitlets.Int(-1).tag(sync=True)
    clicked_bond_indices = traitlets.Tuple((-1, -1)).tag(sync=True)
    _atom_colors = traitlets.Dict({}).tag(sync=True)
    width = traitlets.Float().tag(sync=True)
    height = traitlets.Float().tag(sync=True)
    selected_atoms = traitlets.List([]).tag(sync=True)

    def __init__(self, atoms,
                 charge=-150,
                 width=400, height=350,
                 **kwargs):
        super(MolViz2DBaseWidget, self).__init__(width=width,
                                                 height=height,
                                                 **kwargs)
        try:
            self.atoms = atoms.atoms
        except AttributeError:
            self.atoms = atoms
        else:
            self.entity = atoms
        self.width = width
        self.height = height
        self.uuid = 'mol2d'+str(uuid.uuid4())
        self.charge = charge
        self._clicks_enabled = False
        self.graph = self.to_graph(self.atoms)

    def to_graph(self, atoms):
        """Turn a set of atoms into a graph
        Should return a dict of the form
        {nodes:[a1,a2,a3...],
        links:[b1,b2,b3...]}
        where ai = {atom:[atom name],color='black',size=1,index:i}
        and bi = {bond:[order],source:[i1],dest:[i2],
                color/category='black',distance=22.0,strength=1.0}
        You can assign an explicit color with "color" OR
        get automatically assigned unique colors using "category"
        """
        raise NotImplementedError("This method must be implemented by the interface class")

    def set_atom_style(self, atoms=None, fill_color=None, outline_color=None):
        if atoms is None:
            indices = range(len(self.atoms))
        else:
            indices = map(self.get_atom_index, atoms)
        spec = {}
        if fill_color is not None: spec['fill'] = translate_color(fill_color, prefix='#')
        if outline_color is not None: spec['stroke'] = translate_color(outline_color, prefix='#')
        self.viewer('setAtomStyle', [indices, spec])

    def set_bond_style(self, bonds, color=None, width=None, dash_length=None, opacity=None):
        """
        :param bonds: List of atoms
        :param color:
        :param width:
        :param dash_length:
        :return:
        """
        atom_pairs = [map(self.get_atom_index, pair) for pair in bonds]
        spec = {}
        if width is not None: spec['stroke-width'] = str(width)+'px'
        if color is not None: spec['stroke'] = color
        if dash_length is not None: spec['stroke-dasharray'] = str(dash_length)+'px'
        if opacity is not None: spec['opacity'] = opacity
        if not spec: raise ValueError('No bond style specified!')
        self.viewer('setBondStyle', [atom_pairs, spec])

    def set_atom_label(self, atom, text=None, text_color=None, size=None, font=None):
        atomidx = self.get_atom_index(atom)
        self._change_label('setAtomLabel', atomidx, text, text_color, size, font)

    def set_bond_label(self, bond, text=None, text_color=None, size=None, font=None):
        bondids = map(self.get_atom_index, bond)
        self._change_label('setBondLabel', bondids, text, text_color, size, font)

    def _change_label(self, driver_function, obj_index, text,
                      text_color, size, font):
        spec = {}
        if size is not None:
            if type(size) is not str:
                size = str(size)+'pt'
                spec['font-size'] = size
        if text_color is not None:
            spec['fill'] = text_color  # this strangely doesn't always work if you send it a name
        if font is not None:
            spec['font'] = font
        self.viewer(driver_function, [obj_index, text, spec])

    def highlight_atoms(self, atoms):
        indices = map(self.get_atom_index, atoms)
        self.viewer('updateHighlightAtoms', [indices])

    def get_atom_index(self, atom):
        raise NotImplemented("This method must be implemented by the interface class")

    def set_click_callback(self, callback=None, enabled=True):
        """
        :param callback: Callback can have signature (), (trait_name), (trait_name,old), or (trait_name,old,new)
        :type callback: callable
        :param enabled:
        :return:
        """
        if not enabled: return  # TODO: FIX THIS
        assert callable(callback)
        self._clicks_enabled = True
        self.on_trait_change(callback, 'clicked_atom_index')
        self.click_callback = callback

    def set_color(self, color, atoms=None, render=None):
        self.set_atom_style(fill_color=color, atoms=atoms)

    def set_colors(self, colormap, render=True):
        """
        Args:
         colormap(Mapping[str,List[Atoms]]): mapping of colors to atoms
        """
        for color, atoms in colormap.iteritems():
            self.set_color(atoms=atoms, color=color)


class AlwaysBenzene(MolViz2DBaseWidget):
    def to_graph(self, atoms):
        self.atoms = range(12)
        nodes = [{'atom': 'C', 'category': i, 'index': i}
                 for i in xrange(6)]+ \
                [{'atom': 'H', 'color': 'green', 'index': i+6}
                 for i in xrange(6)]
        links = [{'source': i, 'target': (i+1)%6,
                  'bond': (i%2+1), 'category': i}
                 for i in xrange(6)]+ \
                [{'source': i, 'target': i+6,
                  'bond': 1, 'color': 'blue'}
                 for i in xrange(6)]
        return dict(nodes=nodes, links=links)

    def get_atom_index(self, atom): return atom
