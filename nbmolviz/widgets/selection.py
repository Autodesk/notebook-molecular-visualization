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
import collections

import ipywidgets as ipy
import traitlets
from moldesign import utils

from ..uielements.components import HBox
from .components import ViewerToolBase


class SelBase(ViewerToolBase):
    def __init__(self, mol):
        super().__init__(mol)

        self._atomset = collections.OrderedDict()

        self.atom_listname = ipy.Label('Selected atoms:', layout=ipy.Layout(width='100%'))
        self.atom_list = ipy.SelectMultiple(options=list(self.viewer.selected_atom_indices),
                                            layout=ipy.Layout(height='150px'))
        traitlets.directional_link(
            (self.viewer, 'selected_atom_indices'),
            (self.atom_list, 'options'),
            self._atom_indices_to_atoms
        )

        self.select_all_atoms_button = ipy.Button(description='Select all atoms')
        self.select_all_atoms_button.on_click(self.select_all_atoms)

        self.select_none = ipy.Button(description='Clear all selections')
        self.select_none.on_click(self.clear_selections)

        self.representation_buttons = ipy.ToggleButtons(options=['stick','ribbon', 'auto', 'vdw'],
                                                        value='auto')
        self.representation_buttons.observe(self._change_representation, 'value')

    def remove_atomlist_highlight(self, *args):
        self.atom_list.value = tuple()

    @staticmethod
    def atomkey(atom):
        return '%s (index %d)' % (atom.name, atom.index)

    def _atom_indices_to_atoms(self, atom_indices):
        return [self.mol.atoms[atom_index] for atom_index in atom_indices]

    def select_all_atoms(self, *args):
        self.viewer.selected_atom_indices = [atom.index for atom in self.mol.atoms]

    def clear_selections(self, *args):
        self.viewer.selected_atom_indices = []

    def _change_representation(self, *args):
        repval = self.representation_buttons.value
        if repval == 'auto':
            self.viewer.autostyle()
        elif repval in ('stick', 'ribbon', 'vdw'):
            getattr(self.viewer, repval)()
        else:
            assert False, 'Unknown representation "%s"' % repval


@utils.exports
class AtomSelector(SelBase):
    def __init__(self, mol):
        super().__init__(mol)
        self.subtools.children = [self.representation_buttons]
        self.toolpane.children = [HBox([self.select_all_atoms_button, self.select_none]),
                                  self.atom_listname,
                                  self.atom_list]


@utils.exports
class BondSelector(SelBase):
    def __init__(self, mol):
        super().__init__(mol)

        self._bondset = collections.OrderedDict()
        self._drawn_bond_state = set()

        self.bond_listname = ipy.Label('Selected bonds:', layout=ipy.Layout(width='100%'))
        self.bond_list = ipy.SelectMultiple(options=list(),
                                            layout=ipy.Layout(height='150px'))
        self.viewer.observe(self._update_bondlist, 'selected_atom_indices')

        self.atom_list.observe(self.remove_bondlist_highlight, 'value')

        self.subtools.children = [HBox([self.select_all_atoms_button,
                                        self.select_none])]
        self.toolpane.children = (self.atom_listname,
                                  self.atom_list,
                                  self.bond_listname,
                                  self.bond_list)

    @property
    def selected_bonds(self):
        bonds = []
        atom_indices = set(self.selected_atom_indices)
        for bond in self.mol.bonds:
            if bond.a1.index in atom_indices and bond.a2.index in atom_indices:
                bonds.append(bond)
        return bonds

    @selected_bonds.setter
    def selected_bonds(self, bonds):
        atom_indices = set()
        for b in bonds:
            atom_indices.update((b.a1.index, b.a2.index))
        self.selected_atom_indices = list(sorted(atom_indices))

    def _update_bondlist(self, *args):
        self.bond_list.options = self.selected_bonds

    def _redraw_selection_state(self):
        currentset = set(self._bondset)

        to_turn_on = currentset.difference(self._drawn_bond_state)
        to_turn_off = self._drawn_bond_state.difference(currentset)

        self.bond_list.options = collections.OrderedDict((self.bondkey(bond), bond) for bond in self._bondset)
        super()._redraw_selection_state()
        self._drawn_bond_state = currentset
        self.remove_atomlist_highlight()

    def remove_bondlist_highlight(self, *args):
        self.bond_list.value = tuple()

    @staticmethod
    def bondkey(bond):
        return bond.name

    def clear_selections(self, *args):
        super().clear_selections(*args)


@utils.exports
class ResidueSelector(SelBase):
    """
    Selections at the atom/residue/chain level.
    Selecting a residue selects all of its atoms.
    Selecting all atoms of a residue is equivalent to selecting the residue.
    A residue is not selected if only some of its atoms are selected.
    """

    def __init__(self, mol):
        super().__init__(mol)

        self.selection_type = ipy.Dropdown(description='Clicks select:',
                                           value=self.viewer.selection_type,
                                           options=('Atom', 'Residue', 'Chain'))

        traitlets.link((self.selection_type, 'value'), (self.viewer, 'selection_type'))

        self.residue_listname = ipy.Label('Selected residues:', layout=ipy.Layout(width='100%'))
        self.residue_list = ipy.SelectMultiple(options=list(), height='150px')
        self.viewer.observe(self._update_reslist, 'selected_atom_indices')

        self.residue_list.observe(self.remove_atomlist_highlight, 'value')
        self.atom_list.observe(self.remove_reslist_highlight, 'value')

        self.subtools.children = [self.representation_buttons]
        self.subtools.layout.flex_flow = 'column'
        self.toolpane.children = [self.selection_type,
                                  HBox([self.select_all_atoms_button, self.select_none]),
                                  self.atom_listname,
                                  self.atom_list,
                                  self.residue_listname,
                                  self.residue_list]

    @property
    def selected_residues(self):
        """ List[moldesign.Residue]: A list of the selected residues.

        A residue is considered selected if all of its atoms are.
        """
        num_selected_in_residue = collections.Counter(atom.residue for atom in self.selected_atoms)
        reslist = [res for res, n_selected_atoms in num_selected_in_residue.items()
                   if n_selected_atoms == res.num_atoms]
        reslist.sort(key=lambda x:x.index)
        return reslist

    @selected_residues.setter
    def selected_residues(self, residues):
        with self.hold_trait_notifications(), self.viewer.hold_trait_notifications():
            newres = set(residues)
            for residue in self.selected_residues:
                if residue not in newres:
                    self.toggle_residue(residue)
            self.viewer.select_residues(residues)

    def _update_reslist(self, *args):
        self.residue_list.options = collections.OrderedDict((str(r), r)
                                                            for r in self.selected_residues)

    def toggle_residue(self, residue):
        self.viewer.toggle_residues([residue])

    def remove_reslist_highlight(self, *args):
        self.atom_list.value = tuple()

    @staticmethod
    def atomkey(atom):
        return '%s (index %d)' % (atom.name, atom.index)

    @staticmethod
    def reskey(residue):
        return '{res.name} in chain "{res.chain.name}"'.format(res=residue)

