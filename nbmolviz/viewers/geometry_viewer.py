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
from io import StringIO

import IPython.display as dsp
import traitlets
from past.builtins import basestring
import numpy as np

import moldesign as mdt
from moldesign import units as u
from moldesign import utils
from moldesign import mathutils

from ..utils import translate_color, in_pixels
from ..base.mdt2json import convert as convert_to_json
from ..colormaps import colormap
from .common import BaseViewer


class GeometryViewer(BaseViewer):
    """
    An Jupyter notebook widget that draws molecules in 3D.

    Notes:
        This class handles only the static atomic positions - trajectory and
        orbital visualizations use this class as a component

    Args:
        mol (moldesign.Molecule): The molecule to draw
        style (str): style string - 'vdw', 'stick', 'ribbon' etc.
        display (bool): display this object immediately?
        width (str or int): css width spec (if str) or width in pixels (if int)
        height (str or int): css height spec (if str) or height in pixels (if int)
        **kwargs (dict): ipywidgets keyword arguments
    """
    AXISCOLORS = {'x':'red', 'y':'green', 'z':'blue'}
    DEFAULT_COLOR_MAP = colormap
    DEF_PADDING = 2.25 * u.angstrom
    DISTANCE_UNITS = u.angstrom
    HIGHLIGHT_COLOR = '#1FF3FE'

    _view_name = traitlets.Unicode('MolWidget3DView').tag(sync=True)
    _model_name = traitlets.Unicode('MolWidget3DModel').tag(sync=True)
    _view_module = traitlets.Unicode('nbmolviz-js').tag(sync=True)
    _model_module = traitlets.Unicode('nbmolviz-js').tag(sync=True)

    atom_labels_shown = traitlets.Bool(False).tag(sync=True)
    background_color = traitlets.Unicode('#545c85').tag(sync=True)
    background_opacity = traitlets.Float(1.0).tag(sync=True)
    cubefile = traitlets.Unicode().tag(sync=True)
    far_clip = traitlets.Float().tag(sync=True)
    height = traitlets.Unicode(sync=True)
    labels = traitlets.List([]).tag(sync=True)
    model_data = traitlets.Dict({}).tag(sync=True)
    near_clip = traitlets.Float().tag(sync=True)
    outline_color = traitlets.Unicode('#000000').tag(sync=True)
    outline_width = traitlets.Float(0.0).tag(sync=True)
    positions = traitlets.List([]).tag(sync=True)
    selected_atom_indices = traitlets.List().tag(sync=True)
    selection_type = traitlets.Unicode('Atom', choices=['Atom', 'Residue', 'Chain']).tag(sync=True)
    shapes = traitlets.List([]).tag(sync=True)
    styles = traitlets.Dict({}).tag(sync=True)
    volumetric_style = traitlets.Dict({}).tag(sync=True)
    width = traitlets.Unicode(sync=True)

    SHAPE_NAMES = {
        'SPHERE': 'Sphere',
        'ARROW': 'Arrow',
        'CYLINDER': 'Cylinder',
    }

    STYLE_NAMES = {'vdw': 'sphere',
                   'licorice': 'stick',
                   'line': 'line',
                   'ribbon': 'cartoon',
                   None: None}

    STYLE_SYNONYMS = {'vdw': 'vdw', 'sphere': 'vdw', 'cpk': 'vdw',
                      'licorice': 'licorice', 'stick': 'licorice', 'tube':'licorice',
                      'ball_and_stick': 'ball_and_stick',
                      'line': 'line',
                      'cartoon': 'ribbon', 'ribbon': 'ribbon',
                      None: None, 'hide': None, 'invisible': None, 'remove': None}

    def __init__(self, mol, style=None, display=False, width='100%', height='400px',
                 **kwargs):
        kwargs.update(width=width, height=height)
        super().__init__(**kwargs)
        self.height = in_pixels(height)
        self.width = in_pixels(width)
        self.atom_colors = {}

        # current state
        self.atom_highlights = []
        self._axis_objects = None
        self._colored_as = {}

        self.add_molecule(mol)
        if style is None:
            self.autostyle()
        else:
            self.set_style(style)

        if display:
            dsp.display(self)

    def __reduce__(self):
        """prevent these from being pickled"""
        return utils.make_none, tuple()

    @property
    def selected_atoms(self):
        """ List[moldesign.Atom]: list of selected atoms
        """
        return [self.mol.atoms[i] for i in self.selected_atom_indices]

    @selected_atoms.setter
    def selected_atoms(self, atoms):
        self.selected_atom_indices = [atom.index for atom in atoms]

    def set_outline(self, width=None, color=None):
        if width is None and not self.outline_width:  # set a default
            width = 0.1
        if width is not None:
            self.outline_width = width
        if color is not None:
            self.outline_color = translate_color(color)

    def autostyle(self):
        """ Attempts to create a reasonably informative default rendering style
        """
        if self.mol.mass <= 500.0 * u.dalton:
            self.stick()
        else:
            cartoon_atoms = []
            line_atoms = []
            stick_atoms = []
            biochains = set()
            for residue in self.mol.residues:
                if residue.type in ('protein', 'dna', 'rna'):
                    biochains.add(residue.chain)

                if residue.type == 'protein':
                    cartoon_atoms.extend(residue.atoms)
                elif residue.type in ('water', 'solvent'):
                    line_atoms.extend(residue.atoms)
                elif residue.type in ('dna', 'rna') and self.mol.num_atoms > 1000:
                    cartoon_atoms.extend(residue.atoms)
                else:  # includes DNA, RNA if molecule is small enough
                    stick_atoms.extend(residue.atoms)

            if cartoon_atoms:
                self.cartoon(atoms=cartoon_atoms)
                if len(biochains) > 1:
                    self.color_by('chain', atoms=cartoon_atoms, save=False)
                else:
                    self.color_by('residue.resname', atoms=cartoon_atoms, save=False)
            if line_atoms:
                self.line(atoms=line_atoms)
            if stick_atoms:
                self.stick(atoms=stick_atoms)

        # Deal with unbonded atoms (they only show up in VDW rep)
        if self.mol.num_atoms < 1000:
            lone = [atom for atom in self.mol.atoms if atom.num_bonds == 0]
            if lone:
                self.vdw(atoms=lone, radius=0.5)

    def show_unbonded(self, radius=0.5):
        """ Highlights all unbonded atoms as spheres.

        Useful for rendering styles that do not otherwise show unbonded atoms.

        Args:
            radius (Scalar[length]): radius of the spheres (default 0.5 angstrom)
        """
        lone = [atom for atom in self.mol.atoms if atom.num_bonds == 0]
        if lone: self.vdw(atoms=lone, radius=radius)

    @staticmethod
    def _atoms_to_json(atomlist):
        if hasattr(atomlist, 'iteratoms'):
            idxes = [a.index for a in atomlist.iteratoms()]
        else:
            # TODO: verify that these are actually atoms and not something else with a .index
            idxes = [a.index for a in atomlist]
        atomsel = {'index': idxes}
        return atomsel

    def get_input_file(self):
        if len(self.mol.atoms) <= 250:
            fmt = 'sdf'
        else:
            fmt = 'pdb'
        if not hasattr(self.mol, 'write'):
            writemol = mdt.Molecule(self.mol)
        else:
            writemol = self.mol
        instring = writemol.write(format=fmt)
        return instring, fmt

    def convert_style_name(self, name):
        canonical_name = self.STYLE_SYNONYMS[name]
        if canonical_name in self.STYLE_NAMES:
            return self.STYLE_NAMES[canonical_name]
        else:
            return canonical_name

    # Standard view actions
    def add_molecule(self, mol):
        self.mol = mol
        self.model_data = convert_to_json(self.mol)
        self.set_positions()

    def set_background_color(self, color, opacity=1.0):
        color = translate_color(color)
        self.background_color = color
        self.background_opacity = opacity

    def set_color(self, colors, atoms=None, save=True):
        """ Set atom colors

        May be called in several different ways:
          - ``set_color(color, atoms=list_of_atoms_or_None)``
                  where all passed atoms are to be colored a single color
          - ``set_color(list_of_colors, atoms=list_of_atoms_or_None)``
                  with a list of colors for each atom
          -  ``set_color(dict_from_atoms_to_colors)``
                  a dictionary that maps atoms to colors
          - ``set_color(f, atoms=list_of_atoms_or_None)``
                 where f is a function that maps atoms to colors

        Args:
            colors (see note for allowable types): list of colors for each atom, or map
               from atoms to colors, or a single color for all atoms
            atoms (List[moldesign.Atom]): list of atoms (if None, assumed to be mol.atoms; ignored
               if a dict is passed for "color")
            save (bool): always color these atoms this way (until self.unset_color is called)

        See Also:
            :method:`GeometryViewer.color_by`` - to automatically color atoms using numerical
               and categorical data
        """
        if hasattr(colors, 'items'):
            atoms, colors = zip(*colors.items())
        elif atoms is None:
            atoms = self.mol.atoms

        if callable(colors):
            colors = map(colors, atoms)
        elif isinstance(colors, basestring) or not hasattr(colors, '__iter__'):
            colors = [colors for atom in atoms]

        for atom,color in zip(atoms, colors):
            c = translate_color(color, '#')
            if save:
                self.atom_colors[atom] = c
            self.styles[str(atom.index)]['color'] = c
        self.send_state('styles')

    set_colors = set_color  # synonym

    def unset_color(self, atoms=None):
        """ Resets atoms to their default colors

        Args:
            atoms (List[moldesign.Atom]): list of atoms to color (if None, this is applied to
               all atoms)
        """
        if atoms is None:
            atoms = self.mol.atoms

        for atom in atoms:
            self.atom_colors.pop(atom, None)
            self.styles[str(atom.index)].pop('color', None)
        self.send_state('styles')

    @staticmethod
    def _update_atom_colors(colors, atoms, styles):
        """ Updates list of atoms with the given colors. Colors will be translated to hex.

        Args:
            color (List[str]): list of colors for each atom
            atoms (List[moldesign.Atom]): list of atoms to apply the colors to
            styles (dict): old style dictionary
        """
        styles = dict(styles)

        if len(colors) != len(atoms):
            raise ValueError("Number of colors provided does not match number of atoms provided")

        for atom, color in zip(atoms, colors):
            if str(atom.index) in styles:
                styles[str(atom.index)] = dict(styles[str(atom.index)])
            else:
                styles[str(atom.index)] = {}
            styles[str(atom.index)]['color'] = translate_color(color, prefix='#')

        return styles

    # some convenience synonyms
    def sphere(self, atoms=None, color=None, opacity=None, radius=None):
        """ Draw as Van der Waals spheres

        Args:
            atoms (List[moldesign.Atom]): atoms to apply this style to
               (if not passed, uses all atoms)
            color (int or str): color as string or RGB hexadecimal
            opacity (float): opacity of the representation (between 0 and 1.0)
            radius (float or Scalar[length]): explicit sphere radii (assumes angstrom if no units);
               default: bondi VDW radii
        """
        return self.set_style('vdw', atoms=atoms, color=color, opacity=opacity, radius=radius)
    vdw = cpk = spheres = sphere

    @utils.kwargs_from(sphere)
    def ball_and_stick(self, **kwargs):
        """Draw as balls and sticks

        Args:
            **kwargs (dict): style kwargs
        """
        raise NotImplementedError()  # disabled until we do a couple fixes to the API
    balls_and_sticks = ball_and_stick

    @utils.kwargs_from(sphere)
    def licorice(self, **kwargs):
        """Draw as 3D sticks

        Args:
            **kwargs (dict): style kwargs
        """
        return self.set_style('licorice', **kwargs)
    stick = sticks = tube = tubes = licorice

    @utils.kwargs_from(sphere)
    def line(self, **kwargs):
        """Draw as 1-dimensional lines

        Args:
            **kwargs (dict): style kwargs
        """
        return self.set_style('line', **kwargs)
    lines = line

    @utils.kwargs_from(sphere)
    def ribbon(self, **kwargs):
        return self.set_style('cartoon', **kwargs)
    cartoon = ribbons = ribbon

    def hide(self, atoms=None):
        """ Make these atoms invisible

        Args:
            atoms (List[moldesign.Atom]): atoms to apply this style to
               (if not passed, uses all atoms)
        """
        return self.set_style(None,atoms=atoms)
    off = invisible = hide

    def set_style(self, style, atoms=None, **options):
        self._change_style(style, atoms, True, options)

    def add_style(self, style, atoms=None, **options):
        self._change_style(style, atoms, False, options)

    def _change_style(self, style_string, atoms, replace, options):
        style = self.convert_style_name(style_string)

        # No atoms passed means all atoms
        if atoms is None:
            atoms = self.mol.atoms

        newstyles = self.styles.copy()
        for atom in atoms:
            new_style = {'visualization_type': style}
            for key in ('radius', 'opacity'):
                if options.get(key, None) is not None:
                    new_style[key] = options[key]

            if 'color' in options and options['color'] is not None:
                new_style['color'] = translate_color(options['color'], '#')
                if atom in self.atom_colors and new_style['color'] != self.atom_colors[atom]:
                    self.atom_colors.pop(atom)  # if color is overriden, get rid of it now
            elif atom in self.atom_colors:
                new_style['color'] = self.atom_colors[atom]
            newstyles[str(atom.index)] = new_style

        self.styles = newstyles

    def set_positions(self, positions=None):
        """ Set positions of atoms in the 3D display

        Args:
            positions (Matrix[length, shape=(*,3)]): positions to set atoms to - optional.
               If not provided, positions are taken from current positions of the molecule.

        Returns:

        """
        if positions is None:
            pos = self.mol.positions
        else:
            pos = positions

        self.positions = pos.value_in(u.angstrom).tolist()
        self._update_clipping(np.abs(pos.value_in(self.DISTANCE_UNITS)).max())

    def draw_atom_vectors(self, vecs, rescale_to=1.75,
                          scale_factor=None, opacity=0.85,
                          radius=0.11, **kwargs):
        """ Draw a 3D vector on each atom

        Args:
            vecs (Matrix[shape=(*,3)]): list of vectors for each atom
            rescale_to (Scalar[length]): vectors so the largest is this long
            scale_factor (Scalar[length/units]): factor for conversion between input units and
               length
            kwargs (dict): keyword arguments for self.draw_arrow
        """
        kwargs['radius'] = radius
        kwargs['opacity'] = opacity
        if vecs.shape == (self.mol.ndims,):
            vecs = vecs.reshape(self.mol.num_atoms, 3)
        assert vecs.shape == (self.mol.num_atoms, 3), '`vecs` must be a num_atoms X 3 matrix or' \
                                                      ' 3*num_atoms vector'
        assert not np.allclose(vecs, 0.0), "Input vectors are 0."

        # strip units and scale the vectors appropriately
        if scale_factor is not None:  # scale all arrows by this quantity
            if (u.get_units(vecs)/scale_factor).dimensionless:  # allow implicit scale factor
                scale_factor = scale_factor/self.DISTANCE_UNITS

            vecarray = vecs/scale_factor
            try:
                arrowvecs = vecarray.value_in(self.DISTANCE_UNITS)
            except AttributeError:
                arrowvecs = vecarray

        else:  # rescale the maximum length arrow length to rescale_to
            try:
                vecarray = vecs.magnitude
                unit = vecs.getunits()
            except AttributeError:
                vecarray = vecs
                unit = ''
            lengths = np.sqrt((vecarray*vecarray).sum(axis=1))
            scale = (lengths.max()/rescale_to)  # units of [vec units] / angstrom
            if hasattr(scale, 'defunits'):
                scale = scale.defunits()
            arrowvecs = vecarray/scale
            print('Arrow scale: {q:.3f} {unit} per {native}'.format(q=scale, unit=unit,
                                                                    native=self.DISTANCE_UNITS))
        shapes = []
        for atom, vecarray in zip(self.mol.atoms, arrowvecs):
            if mathutils.norm(vecarray) < 0.2:
                continue
            shapes.append(self.draw_arrow(atom.position, vector=vecarray, **kwargs))
        return shapes

    def draw_axis(self, on=True):
        label_kwargs = dict(color='white', opacity=0.4, fontsize=14)
        if on and self._axis_objects is None:
            xarrow = self.draw_arrow([0, 0, 0], [1, 0, 0], color=self.AXISCOLORS['x'])
            xlabel = self.draw_label([1.0, 0.0, 0.0], text='x', **label_kwargs)
            yarrow = self.draw_arrow([0, 0, 0], [0, 1, 0], color=self.AXISCOLORS['y'])
            ylabel = self.draw_label([-0.2, 1, -0.2], text='y', **label_kwargs)
            zarrow = self.draw_arrow([0, 0, 0], [0, 0, 1], color=self.AXISCOLORS['z'])
            zlabel = self.draw_label([0, 0, 1], text='z', **label_kwargs)
            self._axis_objects = [xarrow, yarrow, zarrow,
                                  xlabel, ylabel, zlabel]

        elif not on and self._axis_objects is not None:
            for arrow in self._axis_objects:
                self.remove(arrow)
            self._axis_objects = None

    draw_axes = draw_axis  # If I can never keep this straight, I doubt anyone else can either ...

    def draw_forces(self, **kwargs):
        return self.draw_atom_vectors(self.mol.forces, **kwargs)

    def draw_momenta(self, **kwargs):
        return self.draw_atom_vectors(self.mol.momenta, **kwargs)

    def highlight_atoms(self, atoms=None):
        """ Highlight a subset of atoms in the system

        Args:
            atoms (list[Atoms]): list of atoms to highlight. If None, remove all highlights
        """
        # TODO: Need to handle style changes
        if self.atom_highlights:  # first, unhighlight old highlights
            to_unset = []
            for atom in self.atom_highlights:
                if atom in self._colored_as:
                    self.set_color(atoms=[atom],
                                   color=self._colored_as[atom],
                                   _store=False)
                else:
                    to_unset.append(atom)

            if to_unset:
                self.atom_highlights = []
                self.unset_color(to_unset, _store=False)

        self.atom_highlights = utils.if_not_none(atoms, [])
        self._redraw_highlights()

    def _redraw_highlights(self):
        if self.atom_highlights:
            self.set_color(self.HIGHLIGHT_COLOR, self.atom_highlights, _store=False)

    @property
    def orbital_is_selected(self):
        return self.current_orbital is not None and self.current_orbital[1] is not None

    def _convert_length(self, obj):
        try:
            return obj.value_in(self.DISTANCE_UNITS)
        except AttributeError:
            if isinstance(obj, (list, tuple)):
                return np.array(obj)
            else:
                return obj
        except u.DimensionalityError:
            if obj.dimensionless:
                return obj.magnitude
            else:
                raise

    def _list_to_jsvec(self, vec):
        assert len(vec) == 3
        try:
            v = self._convert_length(vec)
        except AttributeError:
            v = vec
        return dict(x=v[0], y=v[1], z=v[2])

    def draw_sphere(self, center, radius=2.0, color='red', opacity=1.0):
        """ Draw a 3D sphere into the scene

        Args:
            center (Vector[length, len=3]): center of the sphere
            radius (Scalar[length]): radius of the sphere
            color (str or int): color name or RGB hexadecimal
            opacity (float): sphere opacity

        Returns:
            dict: sphere spec object
        """
        center = self._convert_length(center)
        radius = self._convert_length(radius)
        color = translate_color(color)

        shape = {
            'type': self.SHAPE_NAMES['SPHERE'],
            'center': self._list_to_jsvec(center),
            'radius': radius,
            'color': color,
            'opacity': opacity,
        }
        shapes = list(self.shapes)
        shapes.append(shape)
        self.shapes = shapes
        self._update_clipping(center.max() + radius)
        return shape

    def _update_clipping(self, maxextent):
        self.near_clip = min(self.near_clip, -np.sqrt(3) * maxextent)
        self.far_clip = max(self.far_clip, np.sqrt(3) * maxextent)

    def draw_circle(self, center, normal, radius,
                    color='red', opacity=0.8):
        """ Draw a 2D circle into the scene

        Args:
            center (Vector[length, len=3]): center of the circle
            normal (Vector[len=3]): normal vector
            radius (Scalar[length]): radius of the circle
            color (str or int): color name or RGB hexadecimal
            opacity (float): sphere opacity

        Returns:
            dict: cylinder spec object
        """
        return self._draw3dmol_cylinder(color, center,
                                        np.array(center) + np.array(normal) * 0.01,
                                        True, True,
                                        opacity,
                                        radius)

    def draw_cylinder(self, start, end, radius, color='red', opacity=1.0):
        """ Draw a cylinder into the scene

        Args:
            start (Vector[length, len=3]): center of cylinder top
            end (Vector[length, len=3]): center of cylinder bottom
            radius (Scalar[length]): cylinder radius
            color (str or int): color name or RGB hexadecimal
            opacity (float): sphere opacity

        Returns:
            dict: cylinder spec object
        """
        return self._draw3dmol_cylinder(color, start,
                                        end,
                                        True, True,
                                        opacity,
                                        radius)

    def draw_tube(self, start, end, radius,
                  color='red', opacity=1.0):
        """ Draw a tube into the scene

        Args:
            start (Vector[length, len=3]): center of cylinder top
            end (Vector[length, len=3]): center of cylinder bottom
            radius (Scalar[length]): cylinder radius
            color (str or int): color name or RGB hexadecimal
            opacity (float): sphere opacity

        Returns:
            dict: cylinder spec object
        """
        return self._draw3dmol_cylinder(color, start,
                                        end,
                                        False, False,
                                        opacity,
                                        radius)

    def _draw3dmol_cylinder(self, color, start, end,
                            draw_start_face, draw_end_face,
                            opacity, radius):
        color = translate_color(color)
        facestart = self._convert_length(start)
        faceend = self._convert_length(end)
        radius = self._convert_length(radius)

        shape = {
            'type': self.SHAPE_NAMES['CYLINDER'],
            'start': self._list_to_jsvec(facestart),
            'end': self._list_to_jsvec(faceend),
            'radius': radius,
            'color': color,
            'opacity': opacity,
            'fromCap': 1 if draw_start_face else 0,
            'toCap': 1 if draw_end_face else 0
        }
        shapes = list(self.shapes)
        shapes.append(shape)
        self.shapes = shapes
        self._update_clipping(max(facestart.max() + radius, faceend.max()+radius))
        return shape

    def draw_arrow(self, start, end=None, vector=None, radius=0.15, color='red', opacity=1.0):
        """ Draw a 3D arrow into the scene

        Args:
            start (Vector[length, len=3]): 3D coordinates of arrow start
            end (Vector[length, len=3]): 3D coordinates of arrow end
            vector (Vector[length, len=3]): vector between arrow's start and end.
               Can be provided instead of ``end``
            radius (Scalar[length]): radius of the arrow's base
            color (str or int): color name or hexadecimal RGB
            opacity (float): opacity of the arrow (between 0 and 1)

        Returns:
            dict: Shape specification
        """
        start = self._convert_length(start)

        if (end is None) == (vector is None):
            raise ValueError("Either 'end' or 'vector' should be passed, but not both.")
        if end is None:
            end = start + self._convert_length(vector)
        else:
            end = self._convert_length(end)
        facestart = self._convert_length(start)
        faceend = self._convert_length(end)
        color = translate_color(color)

        shape = {
            'type': self.SHAPE_NAMES['ARROW'],
            'start': self._list_to_jsvec(facestart),
            'end': self._list_to_jsvec(faceend),
            'color': color,
            'radius': radius,
            'opacity': opacity,
        }
        shapes = list(self.shapes)
        shapes.append(shape)
        self.shapes = shapes
        self._update_clipping(max(start.max() + radius, end.max()+radius))
        return shape

    def remove_all_shapes(self):
        """ Delete all non-molecular shapes from the scene

        Returns:
            dict: cylinder spec object
        """
        self.shapes = list()

    def remove(self, obj):
        """ Removes a shape or label

        Args:
            obj (dict): shape or label spec
        """
        if obj in self.shapes:
            self.shapes.remove(obj)
            self.send_state('shapes')
        elif obj in self.labels:
            self.labels.remove(obj)
            self.send_state('labels')
        else:
            raise ValueError('Unknown object type %s' % obj['type'])

    def draw_label(self, position, text, background='black',
                   border='black', color='white',
                   fontsize=14, opacity=1.0):
        """ Draw a piece of text into the 3D scene

        Args:
            position (Vector[length, len=3]): location of the top-left corner of the text
            text (str): the text to write into the scene
            border (str or int): color name or RGB hexadecimal of the label border
                (None for no border)
            color (str or int): color name or RGB hexadecimal
            opacity (float): label opacity (between 0.0 and 1.0)

        Returns:
            dict: cylinder spec object
        """
        position = self._convert_length(position)
        color = translate_color(color)
        if background is not None:
            background = translate_color(background)
        spec = dict(position=self._list_to_jsvec(position),
                    fontColor=color,
                    backgroundColor=background,
                    borderColor=border,
                    fontSize=fontsize,
                    backgroundOpacity=opacity,
                    text=text)

        self.labels.append(spec)
        self.send_state('labels')
        self._update_clipping(position.max() + len(text)/5.0)  # assuming 5 chars per angstrom?
        return spec

    def select_residues(self, residues):
        selected_atom_indices = set()
        if isinstance(residues, mdt.Residue):
            residues = [residues]  # backwards compatibility
        for residue in residues:
            for atom in residue.atoms:
                selected_atom_indices.add(atom.index)
        self.selected_atom_indices = list(sorted(selected_atom_indices))

    def toggle_residues(self, residues):
        selected_atom_indices = set(self.selected_atom_indices)
        for residue in residues:
            for atom in residue.atoms:
                if atom.index in selected_atom_indices:
                    selected_atom_indices.remove(atom.index)
                else:
                    selected_atom_indices.add(atom.index)

        self.selected_atom_indices = selected_atom_indices
