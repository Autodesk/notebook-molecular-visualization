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
from builtins import next
import ipywidgets as ipy
import numpy as np

import traitlets
import moldesign as mdt
from moldesign import utils
from moldesign import units as u

from moldesign.utils import exports

from .components import ViewerToolBase, ReadoutFloatSlider
from ..uielements.components import VBox, HBox

BONDDESCRIPTION = '<b>Bond distance</b> <span style="color:{c1}">{a1.name} - {a2.name}</span>'
ANGLEDESCRIPTION = ('<b>Bond angle</b>'
                    '<span style="color:{c1}">{a1.name} - {a2.name}</span> '
                    '- <span style="color:{c2}">{a3.name}</span>')
DIHEDRALDESCRIPTION = ('<b>Dihedral angle</b> <span style="color:{c0}">{a1.name}</span>'
                       ' - <span style="color:{c1}">{a2.name}'
                       ' - {a3.name}</span> '
                       '- <span style="color:{c2}">{a4.name}</span>')

@exports
class GeometryBuilder(ViewerToolBase):
    MAXDIST = 20.0  # TODO: we need to set this dynamically
    NBR2HIGHLIGHT = '#C5AED8'
    NBR1HIGHLIGHT = '#AFC6A8'
    HIGHLIGHTOPACITY = 0.6
    POSFMT = u'{:.1f} \u212B'
    DEGFMT = u'{:.1f}\u00B0'

    def __init__(self, mol):
        super().__init__(mol)

        self._widgetshapes = {}
        self._atom_labels = []

        # All numbers here are assumed angstroms and radians for now ...
        self._highlighted_bonds = []
        self._highlighted_atoms = []

        self.original_position = self.mol.positions.copy()

        self.clear_button = ipy.Button(description='Clear selection')
        self.clear_button.on_click(self.clear_selection)

        self.label_box = ipy.Checkbox(description='Label atoms', value=False)
        self.label_box.observe(self.label_atoms, 'value')

        # Viewer
        self.selection_description = ipy.HTML()
        self.subtools.children = (HBox([self.clear_button, self.label_box]),
                                  self.selection_description)
        traitlets.directional_link(
            (self.viewer, 'selected_atom_indices'),
            (self.selection_description, 'value'),
            self.get_first_atom
        )

        # Atom manipulation tools - self.{x,y,z}_slider
        self.sliders = []
        for dim, name in enumerate('xyz'):
            slider = ReadoutFloatSlider(
                    min=-self.MAXDIST, max=self.MAXDIST,
                    description='<span style="color: {c}"><b>{n}</b><span>'.format(
                            n=name, c=self.viewer.AXISCOLORS[name]),
                    format=self.POSFMT)
            slider.dim = dim
            setattr(self, name + '_slider', slider)
            self.sliders.append(slider)
            slider.observe(self.set_atom_pos, 'value')

        # Bond manipulation tools
        self.rigid_mol_selector = ipy.ToggleButtons(description='Position adjustment',
                                                    options={'selected atoms only':False,
                                                             'rigid molecule':True},
                                                    value=True)

        self.length_slider = ReadoutFloatSlider(min=0.1, max=self.MAXDIST, format=self.POSFMT)
        self.length_slider.observe(self.set_distance, 'value')
        self.angle_slider = ReadoutFloatSlider(min=1.0, max=179.0, step=2.0, format=self.DEGFMT)
        self.angle_slider.observe(self.set_angle, 'value')
        self.dihedral_slider = ReadoutFloatSlider(min=-90.0, max=360.0, step=4.0,
                                                  format=self.DEGFMT)
        self.dihedral_slider.observe(self.set_dihedral, 'value')

        self.bond_tools = VBox((self.rigid_mol_selector,
                                self.length_slider,
                                self.angle_slider,
                                self.dihedral_slider))

        self.movement_selector = ipy.ToggleButtons(description='Move:',
                                                   value='atom',
                                                   options=['atom', 'residue', 'chain'])
        self.atom_tools = VBox((self.movement_selector,
                                self.x_slider,
                                self.y_slider,
                                self.z_slider))

        self.reset_button = ipy.Button(description='Reset geometry')
        self.reset_button.on_click(self.reset_geometry)

        self.tool_holder = VBox()
        self.toolpane.children = (self.tool_holder,
                                  self.reset_button)

        self.viewer.observe(self._set_tool_state,
                            names='selected_atom_indices')

    def get_first_atom(self, atomIndices):
        if len(atomIndices) < 1:
            return ''
        else:
            atom = self.mol.atoms[next(iter(atomIndices))]
            return u"<b>Atom</b> {atom.name} at coordinates " \
                   u"x:{p[0]:.3f}, y:{p[1]:.3f}, z:{p[2]:.3f} \u212B".format(
                       atom=atom, p=atom.position.value_in(u.angstrom))

    def label_atoms(self, *args):
        with self.viewer.hold_trait_notifications():
            if self.label_box.value and not self._atom_labels:
                self._atom_labels = [self.viewer.draw_label(position=atom.position, text=atom.name)
                                     for atom in self.mol.atoms]
            else:
                for l in self._atom_labels:
                    self.viewer.remove(l)
                self._atom_labels = []
        self.viewer.send_state('labels')


    # Returns the first bond indicated by bondIndices
    @staticmethod
    def get_selected_bond(bonds):
        return next(iter(bonds))

    def _set_tool_state(self, *args):
        """ Observes the `viewer.selected_atom_indices` list and updates the tool panel accordingly

        Returns:
            Tuple(ipywidgets.BaseWidget): children of the tool panel
        """
        atoms = self.viewer.selected_atoms
        with self.viewer.hold_trait_notifications():
            for shape in self._widgetshapes.values():
                if shape == '_axes':
                    self.viewer.draw_axes(False)
                else:
                    self.viewer.remove(shape)
            self._widgetshapes = {}

        if len(atoms) == 1:
            self._setup_atom_tools(atoms)
        elif len(atoms) == 2:
            self._setup_distance_tools(atoms)
        elif len(atoms) == 3:
            self._setup_angle_tools(atoms)
        elif len(atoms) == 4:
            self._setup_dihedral_tools(atoms)
        else:
            self.tool_holder.children = (ipy.HTML('Please click on 1-4 atoms'),)

    def _setup_atom_tools(self, atoms):
        atom = atoms[0]
        for slider, val in zip(self.sliders, atom.position.value_in(u.angstrom)):
            with slider.hold_trait_notifications():
                slider.value = val
        self.tool_holder.children = (self.atom_tools,)
        self.viewer.draw_axes(True)
        self._widgetshapes = {'_axes': '_axes'}

    def set_atom_pos(self, change):
        atom = self.selected_atoms[0]
        if self.movement_selector.value == 'atom':
            atom.position[change['owner'].dim] = change['new']*u.angstrom
        else:
            idim = change['owner'].dim
            atom_idxes = [atom.index for atom in getattr(atom, self.movement_selector.value).atoms]
            delta = change['new'] * u.angstrom - atom.position[idim]
            self.viewer.mol.positions[atom_idxes, idim] += delta
        self.viewer.set_positions()

    def _setup_distance_tools(self, atoms):
        a1, a2 = atoms
        self.viewer.shapes = []

        # creates a temp cylinder that will be overwritten in self.set_distance
        self._widgetshapes = {
            'bond':self.viewer.draw_cylinder(a1.position, a2.position, radius=0.3,
                                                        opacity=0.65, color='red')}
        self.length_slider.value = a1.distance(a2).value_in(u.angstrom)
        self.length_slider.description = BONDDESCRIPTION.format(
                a1=a1, a2=a2, c1=self.viewer.HIGHLIGHT_COLOR)

        bond = mdt.Bond(a1, a2)
        if bond.exists and not bond.is_cyclic:
            self.tool_holder.children = (self.rigid_mol_selector, self.length_slider,)
        else:
            self.tool_holder.children = (self.length_slider,)
            self.rigid_mol_selector.value = False

    def set_distance(self, *args):
        a1, a2 = self.viewer.selected_atoms
        dist_in_angstrom = self.length_slider.value
        mdt.set_distance(a1, a2, dist_in_angstrom*u.angstrom,
                         adjustmol=self.rigid_mol_selector.value)
        for endpoint in (self._widgetshapes['bond']['start'],
                         self._widgetshapes['bond']['end']):
            endpoint['x'], endpoint['y'], endpoint['z'] = a1.position.value_in(u.angstrom)

        with self.viewer.hold_trait_notifications():
            self.viewer.send_state('shapes')
            self.viewer.set_positions()

    def _setup_angle_tools(self, atoms):
        a1, a2, a3 = atoms
        self.viewer.shapes = []

        # creates a temp cylinder that will be overwritten in self.set_distance
        angle_normal = np.cross(a1.position-a2.position,
                               a3.position-a2.position)

        self._widgetshapes = {
            'plane': self.viewer.draw_circle(a2.position, normal=angle_normal,
                                             radius=max(a1.distance(a2), a3.distance(a2)),
                                             opacity=0.55, color='blue'),
            'origin': self.viewer.draw_sphere(a2.position,
                                              radius=0.5, opacity=0.85, color='green'),
            'b1': self.viewer.draw_cylinder(a1.position, a2.position, radius=0.3,
                                            opacity=0.65, color='red'),
            'b2': self.viewer.draw_cylinder(a3.position, a2.position, radius=0.3,
                                            opacity=0.65, color='red')}

        self.angle_slider.value = mdt.angle(a1, a2, a3).value_in(u.degrees)
        self.angle_slider.description = ANGLEDESCRIPTION.format(
                    a1=a1, a2=a2, a3=a3,
                    c1=self.viewer.HIGHLIGHT_COLOR, c2=self.NBR2HIGHLIGHT)

        b1 = mdt.Bond(a1, a2)
        b2 = mdt.Bond(a3, a2)
        if b1.is_cyclic:
            b1, b2 = b2, b1  # try to find a b1 that is not cyclic
        if b1.exists and b2.exists and not b1.is_cyclic:
            self.tool_holder.children = (self.rigid_mol_selector, self.angle_slider,)
        else:
            self.tool_holder.children = (self.angle_slider,)
            self.rigid_mol_selector.value = False

    def set_angle(self, *args):
        a1, a2, a3 = self.viewer.selected_atoms
        mdt.set_angle(a1, a2, a3,
                      self.angle_slider.value*u.pi/180.0, adjustmol=self.rigid_mol_selector.value)

        for endpoint, atom in ((self._widgetshapes['b1']['start'], a1),
                               (self._widgetshapes['b2']['start'], a3)):
            endpoint['x'], endpoint['y'], endpoint['z'] = atom.position.value_in(u.angstrom)

        with self.viewer.hold_trait_notifications():
            self.viewer.send_state('shapes')
            self.viewer.set_positions()

    def _setup_dihedral_tools(self, atoms):
        a1, a2, a3, a4 = atoms
        bc = mdt.Bond(a2, a3)
        b_0 = mdt.Bond(a1, a2)
        b_f = mdt.Bond(a3, a4)

        self._widgetshapes = {
            'b1': self.viewer.draw_cylinder(a1.position, a2.position, radius=0.3,
                                            opacity=0.65, color='red'),
            'b3': self.viewer.draw_cylinder(a3.position, a4.position, radius=0.3,
                                            opacity=0.65, color='red'),
            'plane': self.viewer.draw_circle(center=bc.midpoint,
                                             normal=a3.position-a2.position,
                                             radius=1.5, color='blue', opacity=0.55)}

        self.dihedral_slider.description = DIHEDRALDESCRIPTION.format(
                a1=a1, a2=a2, a3=a3, a4=a4,
                c0=self.NBR1HIGHLIGHT, c1=self.viewer.HIGHLIGHT_COLOR,
                c2=self.NBR2HIGHLIGHT)
        if bc.exists and b_0.exists and b_f.exists and not b_0.is_cyclic:
            self.tool_holder.children = (self.rigid_mol_selector, self.dihedral_slider,)
        else:
            self.rigid_mol_selector = False
            self.tool_holder.children = (self.dihedral_slider,)

    def set_dihedral(self, *args):
        a1, a2, a3, a4 = self.viewer.selected_atoms
        mdt.set_dihedral(a1, a2, a3, a4,
                         self.dihedral_slider.value*u.pi/180.0,
                         adjustmol=self.rigid_mol_selector.value)

        for endpoint, atom in ((self._widgetshapes['b1']['start'], a1),
                               (self._widgetshapes['b3']['end'], a4)):
            endpoint['x'], endpoint['y'], endpoint['z'] = atom.position.value_in(u.angstrom)

        with self.viewer.hold_trait_notifications():
            self.viewer.send_state('shapes')
            self.viewer.set_positions()

    def _highlight_atoms(self, atoms, color=None):
        color = utils.if_not_none(color, self.viewer.HIGHLIGHT_COLOR)
        self._highlighted_atoms += atoms
        self.viewer.add_style('vdw', atoms=atoms,
                              radius=self.viewer.ATOMRADIUS * 1.1,
                              color=color,
                              opacity=self.HIGHLIGHTOPACITY)

    def _unhighlight_atoms(self, atoms):
        self.viewer.set_style('vdw', atoms=atoms,
                              radius=self.viewer.ATOMRADIUS)

    def clear_selection(self, *args):
        self.viewer.selected_atom_indices = []

    def reset_geometry(self, *args):
        self.clear_selection()
        self.mol.positions = self.original_position
        self.viewer.set_positions()
