from __future__ import print_function
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()

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
import uuid

from IPython.display import display as dsp
import traitlets
import ipywidgets as ipy
import itertools

import moldesign as mdt
from moldesign import utils
from moldesign import units as u

from . import BaseViewer
from ..utils import translate_color


class ChemicalGraphViewer(BaseViewer):
    """
    Draws 2D molecular representations with D3.js
    """
    MAXATOMS = 200

    _view_name = traitlets.Unicode('MolWidget2DView').tag(sync=True)
    _model_name = traitlets.Unicode('MolWidget2DModel').tag(sync=True)
    _view_module = traitlets.Unicode('nbmolviz-js').tag(sync=True)
    _model_module = traitlets.Unicode('nbmolviz-js').tag(sync=True)

    graph_layout_charge = traitlets.Float(-150.0).tag(sync=True)
    uuid = traitlets.Unicode().tag(sync=True)
    graph = traitlets.Dict().tag(sync=True)
    clicked_bond_indices = traitlets.Tuple((-1, -1)).tag(sync=True)
    _atom_colors = traitlets.Dict({}).tag(sync=True)
    width = traitlets.Float().tag(sync=True)
    height = traitlets.Float().tag(sync=True)
    selected_atom_indices = traitlets.List([]).tag(sync=True)

    def __init__(self, atoms,
                 carbon_labels=True,
                 names=None,
                 width=400, height=350,
                 display=False,
                 _forcebig=False,
                 **kwargs):

        self.atoms = getattr(atoms, 'atoms', atoms)

        if not _forcebig and len(self.atoms) > self.MAXATOMS:
            raise ValueError('Refusing to draw more than 200 atoms in 2D visualization. '
                             'Override this with _forcebig=True')

        if names is None:
            names = []
            for atom in self.atoms:
                if atom.formal_charge == 0:
                    names.append(atom.name)
                else:
                    names.append(atom.name + _charge_str(atom.formal_charge))

        self.names = names

        self.atom_indices = {atom: i for i, atom in enumerate(self.atoms)}
        self.selection_group = None
        self.selection_id = None
        self.width = width
        self.height = height
        self.uuid = 'mol2d'+str(uuid.uuid4())
        self.carbon_labels = carbon_labels
        self._clicks_enabled = False
        self.graph = self.to_graph(self.atoms)

        super().__init__(layout=ipy.Layout(width=str(width), height=str(height)))

        if display: dsp.display(self)

    def __reduce__(self):
        """These don't get passed around,
        so we send NOTHING"""
        return utils.make_none, tuple()

    def to_graph(self, atoms):
        nodes, links = [], []
        for i1, atom1 in enumerate(atoms):
            nodes.append(dict(atom=self.names[i1], index=i1))
            if atom1.atnum == 6 and not self.carbon_labels:
                nodes[-1].update({'atom': '',
                                  'size': 0.5,
                                  'color': 'darkgray'})
            for neighbor, order in atom1.bond_graph.items():
                if neighbor not in self.atom_indices: continue
                nbr_idx = self.atom_indices[neighbor]
                if nbr_idx < i1:
                    links.append({'source': i1,
                                  'target': nbr_idx,
                                  'bond': order})
        graph = dict(nodes=nodes, links=links)
        return graph

    def get_atom_index(self, atom):
        """ Return the atom's index in this object's storage
        """
        return self.atom_indices[atom]

    def unset_color(self, atoms=None, render=None):
        self.set_color('white', atoms)

    def handle_selection_event(self, selection):
        """ Highlight atoms in response to a selection event

        Args:
            selection (dict): Selection event from :mod:`..uibase.selectors`
        """
        if 'atoms' in selection:
            self.highlight_atoms(
                [a for a in selection['atoms'] if a in self.atom_indices])

    def set_atom_style(self, atoms=None, fill_color=None, outline_color=None):
        if atoms is None:
            indices = list(range(len(self.atoms)))
        else:
            indices = list(map(self.get_atom_index, atoms))
        spec = {}
        if fill_color is not None: spec['fill'] = translate_color(fill_color, prefix='#')
        if outline_color is not None: spec['stroke'] = translate_color(outline_color, prefix='#')
        self.viewer('setAtomStyle', [indices, spec])

    def set_bond_style(self, bonds, color=None, width=None, dash_length=None, opacity=None):
        atom_pairs = [list(map(self.get_atom_index, pair)) for pair in bonds]
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
        bondids = list(map(self.get_atom_index, bond))
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
        indices = list(map(self.get_atom_index, atoms))
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
        self.on_trait_change(callback, 'selected_atom_indices')
        self.click_callback = callback

    def set_color(self, color, atoms=None, render=None):
        self.set_atom_style(fill_color=color, atoms=atoms)

    def set_colors(self, colormap):
        """
        Args:
         colormap(Mapping[str,List[Atoms]]): mapping of colors to atoms
        """
        for color, atoms in colormap.items():
            self.set_color(atoms=atoms, color=color)

def _charge_str(q):
    q = q.value_in(u.q_e)
    if q == 0:
        return ''
    elif q == 1:
        return '+'
    elif q == -1:
        return '-'
    elif q > 0:
        return '+%d' % q
    else:
        return str(q)


class DistanceGraphViewer(ChemicalGraphViewer):
    """ Create a 2D graph that includes edges with 3D information. This gives a 2D chemical that
    shows contacts from 3D space.

    Args:
        mol (moldesign.molecules.AtomContainer): A collection of atoms (eg a list of atoms,
            a residue, a molecule. etc)
        distance_sensitivity (Tuple[u.Scalar[length]]): a tuple containing the minimum and
            maximum 3D distances to create edges for (default: ``(3.0*u.ang, 7.0*u.ang)``)
        bond_edge_weight (float): edge weight for covalent bonds
        nonbond_weight_factor (float): scale non-covalent edge weights by this factor
        angstrom_to_px (int): number of pixels per angstrom
        charge (int): the force-directed layout repulsive "charge"
    """
    def __init__(self, atoms,
                 distance_sensitivity=(3.0 * u.angstrom, 7.0 * u.angstrom),
                 bond_edge_weight=1.0,
                 minimum_edge_weight=0.2,
                 nonbond_weight_factor=0.66,
                 angstrom_to_px=22.0,
                 charge=-300,
                 **kwargs):
        dmin, dmax = distance_sensitivity
        self.minimum_bond_strength = minimum_edge_weight
        self.dmin = dmin.value_in(u.angstrom)
        self.dmax = dmax.value_in(u.angstrom)
        self.drange = self.dmax - self.dmin
        self.bond_strength = bond_edge_weight
        self.angstrom_to_px = angstrom_to_px
        self.nonbond_strength = nonbond_weight_factor
        self.colored_residues = {}
        kwargs['charge'] = charge
        super().__init__(atoms, **kwargs)

    def to_graph(self, atoms):
        graph = super().to_graph(atoms)

        # Deal with covalent bonds
        for link in graph['links']:
            a1 = atoms[link['source']]
            a2 = atoms[link['target']]
            link['strength'] = self.bond_strength
            link['distance'] = a1.distance(a2).value_in(
                u.angstrom) * self.angstrom_to_px

        # Add distance restraints for non-bonded atoms
        for i1, atom1 in enumerate(atoms):
            for i2 in range(i1 + 1, len(atoms)):
                atom2 = atoms[i2]
                if atom1 in atom2.bond_graph: continue

                distance = atom1.distance(atom2).value_in(u.angstrom)
                if distance > self.dmax: continue

                strength = self.nonbond_strength * min(
                    float((1.0 -(distance - self.dmin/self.drange)) ** 2),
                    1.0)

                if strength < self.minimum_bond_strength: continue

                link = {'distance': float(distance * self.angstrom_to_px),
                        'source': i1, 'target': i2,
                        'strength': strength, 'bond': 0}
                graph['links'].append(link)

        return graph

    def draw_contacts(self, group1, group2, radius=2.25 * u.angstrom,
                      label=True):
        for atom1, atom2 in itertools.product(group1, group2):
            if atom1.index == atom2.index: continue
            if atom1 in atom2.bond_graph: continue
            skip = False
            for nbr in atom2.bond_graph:
                if atom1 in nbr.bond_graph:
                    skip = True
            if skip: continue
            dst = atom1.distance(atom2)
            if dst <= radius:
                self.set_bond_style([[atom1, atom2]],
                                    width=1, dash_length=1, opacity=1.0, color='black')
                if label:
                    self.set_bond_label([atom1, atom2],
                                        text='%.1f ang'%dst.value_in('angstrom'),size=8)


def make_contact_view(entity, view_radius=5.0*u.angstrom,
                      contact_radius=2.25*u.angstrom,
                      angstrom_to_px=44.0,
                      **kwargs):
    """

    :type entity: moldesign.biounits.BioContainer
    :param kwargs:
    :return:
    """
    from moldesign.molecules import AtomList

    try:
        focus_atoms = AtomList(entity.atoms)
    except AttributeError:
        focus_atoms = AtomList(entity)

    # get the complete set of atoms to display
    view_atoms = focus_atoms.atoms_within(view_radius)
    all_atoms = AtomList(view_atoms + focus_atoms)
    assert len(set(all_atoms)) == len(view_atoms) + len(focus_atoms)
    viewer = DistanceGraphViewer(all_atoms, **kwargs)
    viewer.color_by_residue(black_residue=focus_atoms[0].residue)
    viewer.draw_contacts(focus_atoms, view_atoms, radius=contact_radius)
    return viewer
