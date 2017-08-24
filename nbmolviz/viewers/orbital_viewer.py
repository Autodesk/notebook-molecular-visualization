from __future__ import print_function, absolute_import, division, unicode_literals
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

from IPython.display import display as display_now
import numpy as np
import ipywidgets as ipy
import traitlets
import io

from moldesign import units as u
from moldesign.mathutils import padded_grid

from ..viewers import GeometryViewer, translate_color
from ..widget_utils import process_widget_kwargs
from ..uielements.components import HBox, VBox
from . import ViewerContainer


class OrbitalViewer(ViewerContainer):
    """
    Subclass of the standard geometry viewer with added UI for rendering orbitals

    Args:
        mol (mdt.Molecule): a molecule with A) orbitals, and
                            B) an energy model with calculate_orbital_grid
        display (bool): immediately draw the viewer in the notebook
        **kwargs (dict): kwargs for the viewer
    """
    current_orbital = traitlets.Any()  # reference to the currently displayed orbital
    isoval = traitlets.Float(0.01)
    orb_opacity = traitlets.Float(0.8)
    negative_color = traitlets.Union([traitlets.Integer(), traitlets.Unicode()], default='red')
    positive_color = traitlets.Union([traitlets.Integer(), traitlets.Unicode()], default='blue')
    numpoints = traitlets.Integer(40, default=50, max=120, min=10)

    def __init__(self, mol, display=False, **kwargs):
        self.type_dropdown = None
        self.orblist = None
        self.isoval_selector = None
        self.opacity_selector = None
        self.viewer = GeometryViewer(mol=mol, **process_widget_kwargs(kwargs))
        self.mol = mol
        self.wfn = mol.wfn   # cache this directly because the molecule's state may change
        self._restyle_orbital()  # sets defaults for orbital spec
        self._cached_cubefiles = {}

        self.uipane = self._make_ui_pane(self.viewer.layout.height)
        hb = HBox([self.viewer, self.uipane])
        super().__init__([hb], viewer=self.viewer)
        if display:
            display_now(self)

    def draw_orbital(self, orbital):
        """Display a molecular orbital

        Args:
            orbital (moldesign.orbitals.Orbital): orbital to draw
        """
        # This triggers self._redraw_orbital
        self.current_orbital = orbital

    @traitlets.observe('current_orbital', 'numpoints')
    def _redraw_orbital(self, *args):
        self.status_element.value = '<div class="nbv-loader"/>'
        try:
            if self.current_orbital is None:
                self.viewer.cubefile = ''
                return

            orbkey = (id(self.current_orbital), self.numpoints)

            if orbkey not in self._cached_cubefiles:
                grid, values = self._calc_orb_grid(self.current_orbital)
                cubefile = self._grid_to_cube(grid, values)
                self._cached_cubefiles[orbkey] = cubefile
            else:
                cubefile = self._cached_cubefiles[orbkey]

            self.viewer.cubefile = cubefile
        except Exception as e:
            self.status_element.value = u'⚠ %s' % e
        else:
            self.status_element.value = ''


    @traitlets.observe('negative_color',
                       'positive_color',
                       'isoval',
                       'orb_opacity')
    def _restyle_orbital(self, *args):
        # this triggers the redraw
        self.viewer.volumetric_style = {
            'iso_val': self.isoval,
            'opacity': self.orb_opacity,
            'negativeVolumetricColor': self.negative_color,
            'positiveVolumetricColor': self.positive_color}

    def _calc_orb_grid(self, orbital):
        """ Calculate grid of values for this orbital

        Args:
            orbital (moldesign.Orbital): orbital to calcualte grid for

        Returns:
            VolumetricGrid: grid that amplitudes where computed on
            Vector[1/length**1.5]: list of orbital amplitudes at each point on grid
        """
        # NEWFEATURE: limit grid size based on the non-zero atomic centers. Useful for localized
        #    orbitals, which otherwise require high resolution
        grid = padded_grid(self.wfn.positions,
                           padding=3.0 * u.angstrom,
                           npoints=self.numpoints)
        with np.errstate(under='ignore'):
            values = orbital(grid.allpoints())
        return grid, values

    @staticmethod
    def _grid_to_cube(grid, values):
        """ Given a grid of values, create a gaussian cube file

        Args:
            grid (utils.VolumetricGrid): grid of points
            values (Iterable): iterator over grid values, in the same order as grid points

        Returns:
            str: contents of the cube file
        """
        fobj = io.StringIO()

        # First two header lines
        print('CUBE File\nGenerated by nbmolviz', file=fobj)

        # third line: number of atoms (0, here) + origin of grid
        print('-1 %f %f %f' % tuple(grid.origin.value_in(u.angstrom)), file=fobj)

        # lines 4-7: number of points in each direction and basis vector for each
        # basis vectors are negative to indicate angstroms
        print('%d %f 0.0 0.0' % (-grid.xpoints, grid.dx.value_in(u.angstrom)), file=fobj)
        print('%d 0.0 %f 0.0' % (-grid.ypoints, grid.dy.value_in(u.angstrom)), file=fobj)
        print('%d 0.0 0.0 %f' % (-grid.zpoints, grid.dz.value_in(u.angstrom)), file=fobj)

        # Next is a line per atom
        # We put just one atom here - it shouldn't be rendered
        print('6 0.000 0.0 0.0 0.0', file=fobj)

        # Next, indicate that there's just one orbital
        print('1 1', file=fobj)

        # finally, write out all the grid values
        # ival = 0
        valueiter = iter(values)
        for ix in range(grid.xpoints):
            for iy in range(grid.ypoints):
                for iz in range(grid.zpoints):
                    print(str(next(valueiter)), end=' ', file=fobj)
                    # ival += 1
                    # if ival%6 == 0: print >> fobj #newline
                    if iz % 6 == 5:
                        fobj.write('\n')
                fobj.write('\n')

        v = fobj.getvalue()
        fobj.close()
        return v

    def _make_ui_pane(self, hostheight):
        layout = ipy.Layout(width='325px',
                            height=str(int(hostheight.rstrip('px')) - 50) + 'px')
        #element_height = str(int(hostheight.rstrip('px')) - 125) + 'px'
        element_height = None
        # NOTE - element_height was used for the listbox-style orblist.
        #   HOWEVER ipywidgets 6.0 only displays those as a dropdown.
        #   This is therefore disabled until we can display listboxes again. -- AMV 7/16

        # Orbital set selector
        self.status_element = ipy.HTML(layout=ipy.Layout(width='inherit', height='20px'))
        orbtype_label = ipy.Label("Orbital set:")
        self.type_dropdown = ipy.Dropdown(options=list(self.wfn.orbitals.keys()))
        initialtype = 'canonical'
        if initialtype not in self.type_dropdown.options:
            initialtype = next(iter(self.type_dropdown.options.keys()))
        self.type_dropdown.value = initialtype
        self.type_dropdown.observe(self.new_orb_type, 'value')

        # List of orbitals in this set
        orblist_label = ipy.Label("Orbital:")
        self.orblist = ipy.Dropdown(options={None: None},
                                    layout=ipy.Layout(width=layout.width, height=element_height))
        traitlets.link((self.orblist, 'value'), (self, 'current_orbital'))

        # Isovalue selector
        isoval_label = ipy.Label('Isovalue:')
        self.isoval_selector = ipy.FloatSlider(min=0.0, max=0.075,
                                               value=0.01, step=0.00075,
                                               readout_format='.4f',
                                               layout=ipy.Layout(width=layout.width))
        traitlets.link((self.isoval_selector, 'value'), (self, 'isoval'))

        # Opacity selector
        opacity_label = ipy.Label('Opacity:')
        self.opacity_selector = ipy.FloatSlider(min=0.0, max=1.0,
                                               value=0.8, step=0.01,
                                               readout_format='.2f',
                                               layout=ipy.Layout(width=layout.width))
        traitlets.link((self.opacity_selector, 'value'), (self, 'orb_opacity'))

        # Resolution selector
        resolution_label = ipy.Label("Grid resolution:", layout=ipy.Layout(width=layout.width))
        self.orb_resolution = ipy.Text(layout=ipy.Layout(width='75px',
                                                         positioning='bottom'))
        self.orb_resolution.value = str(self.numpoints)
        self.resolution_button = ipy.Button(description='Update resolution')
        self.resolution_button.on_click(self.change_resolution)
        traitlets.directional_link((self, 'numpoints'), (self.orb_resolution, 'value'),
                                   transform=str)

        self.uipane = ipy.VBox([self.status_element,
                                orbtype_label, self.type_dropdown,
                                orblist_label, self.orblist,
                                isoval_label, self.isoval_selector,
                                opacity_label, self.opacity_selector,
                                resolution_label, self.orb_resolution, self.resolution_button])
        self.new_orb_type()
        self.type_dropdown.observe(self.new_orb_type, 'value')
        return self.uipane

    def new_orb_type(self, *args):
        """Create list of available orbitals when user selects a new type
        """
        wfn = self.wfn
        newtype = self.type_dropdown.value
        neworbs = wfn.orbitals[newtype]
        orblist = collections.OrderedDict()

        orblist[None] = None
        for i, orb in enumerate(neworbs):
            if hasattr(orb, 'unicode_name'):
                orbname = orb.unicode_name
            else:
                orbname = orb.name

            meta = ''
            if orb.energy is not None:
                meta = '{:.02fP}'.format(orb.energy.defunits())
            if orb.occupation is not None:
                if meta: meta += ', '
                meta += 'occ %.2f' % orb.occupation
            if meta:
                desc = '%d. %s   (%s)' % (i, orbname, meta)
            else:
                desc = '%d. %s' % (i, orbname)
            orblist[desc] = orb
        self.orblist.value = None
        self.orblist.options = orblist

    def change_resolution(self, *args):
        self.numpoints = int(self.orb_resolution.value)
