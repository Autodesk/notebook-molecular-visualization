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
import numpy as np
from StringIO import StringIO
from traitlets import Float, Unicode

from nbmolviz.utils import JSObject, translate_color
from nbmolviz.widget3d import MolViz3DBaseWidget


class MolViz_3DMol(MolViz3DBaseWidget):
    _view_name = Unicode('MolWidget3DView').tag(sync=True)
    _model_name = Unicode('MolWidget3DModel').tag(sync=True)
    _view_module = Unicode('nbmolviz-js').tag(sync=True)
    _model_module = Unicode('nbmolviz-js').tag(sync=True)
    model_data = Unicode('').tag(sync=True)
    model_data_format = Unicode('').tag(sync=True)
    background_color = Unicode('0x73757C').tag(sync=True)
    background_opacity = Float(1.0).tag(sync=True)

    STYLE_NAMES = {'vdw': 'sphere',
                   'licorice': 'stick',
                   'line': 'line',
                   'ribbon': 'cartoon',
                   None: None}

    def __init__(self, *args, **kwargs):
        super(MolViz_3DMol, self).__init__(*args, **kwargs)
        self.current_orbital = None
        self.orbital_spec = {}
        self.current_js_orbitals = []
        self._cached_voldata = {}
        self._clicks_enabled = False
        self.click_callback = None

    # Utilities
    def convert_style_name(self, name):
        canonical_name = self.STYLE_SYNONYMS[name]
        if canonical_name in self.STYLE_NAMES:
            return self.STYLE_NAMES[canonical_name]
        else:
            return canonical_name

    # Standard view actions
    def add_molecule(self, mol):
        self.mol = mol
        moldata, format = self.get_input_file()
        self.model_data_format = format
        self.model_data = moldata
        self.set_style('sphere')
        if self.click_callback is not None:
            self.viewer('makeAtomsClickable', [])

    def set_background_color(self, color, opacity=1.0):
        color = translate_color(color)
        self.background_color = color
        self.background_opacity = opacity

    def set_style(self, style, atoms=None, **options):
        backend_call = 'setStyle'
        self._change_style(backend_call, style, atoms, options)

    def set_color(self, color, atoms=None):
        atom_json = self._atoms_to_json(atoms)
        color = translate_color(color)
        self.viewer('setAtomColor', [atom_json, color])

    def set_clipping(self, near, far):
        self.viewer('setSlab', [float(near), float(far)])

    def set_colors(self, colormap):
        """
        Args:
         colormap(Mapping[str,List[Atoms]]): mapping of colors to atoms
        """
        json = {}
        for color, atoms in colormap.iteritems():
            json[translate_color(color)] = self._atoms_to_json(atoms)
        self.viewer('setColorArray', [json,])

    def unset_color(self, atoms=None):
        if atoms is None:
            atom_json = {}
        else:
            atom_json = self._atoms_to_json(atoms)
        self.viewer('unsetAtomColor', [atom_json])

    def add_style(self, style, atoms=None, **options):
        backend_call = 'addStyle'
        self._change_style(backend_call, style, atoms, options)

    def _change_style(self, backend_call, style_string,
                      atoms, options):
        if atoms is None:
            atom_json = {}
        else:
            atom_json = self._atoms_to_json(atoms)

        if 'color' in options:
            try:
                options['color'] = translate_color(options['color'])
            except AttributeError:
                pass

        style = self.convert_style_name(style_string)
        if style is None:
            style_spec = {}
        else:
            style_spec = {style: options}

        self.viewer(backend_call, [atom_json, style_spec])

    def append_frame(self, positions=None):
        if positions is None:
            positions = self.get_positions()

        positions = self._convert_units(positions)
        try:
            positions = positions.tolist()
        except AttributeError:
            pass

        self.num_frames += 1
        self.viewer('addFrameFromList', args=[positions])
        self.show_frame(self.num_frames - 1)

    def set_positions(self, positions=None):
        if positions is None:
            positions = self.get_positions()
        self.viewer('setPositions',[positions])

    def show_frame(self, framenum):
        self.viewer('setFrame', [framenum])
        self.current_frame = framenum
        if self.current_orbital is not None:
            self.draw_orbital(self.current_orbital, **self.orbital_spec)

    # Interaction
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
        self.on_trait_change(callback, '_click_selection')
        self.click_callback = callback
        self.viewer('makeAtomsClickable', [])

    #Shapes
    @staticmethod
    def _list_to_jsvec(vec):
        assert len(vec) == 3
        return dict(x=vec[0], y=vec[1], z=vec[2])

    def draw_sphere(self, position,
                    radius=2.0, color='red',
                    opacity=1.0, clickable=False):
        js_shape = JSObject('shape')
        position = self._convert_units(position)
        radius = self._convert_units(radius)
        center = dict(x=position[0], y=position[1], z=position[2])
        color = translate_color(color)

        self.viewer('renderPyShape', ['Sphere',
                                      dict(center=center, radius=radius,
                                           color=color, alpha=opacity),
                                      js_shape.id,
                                      clickable])
        return js_shape

    def draw_circle(self, center, normal, radius,
                    color='red', opacity=0.8, clickable=False,
                    batch=False):
        # TODO: this doesn't work! appears to be a bug in 3dmol.js
        # return self._draw3dmol_cylinder(color, center,
        #                                np.array(center) + np.array(normal) * 0.01,
        #                                True, False,
        #                                opacity,
        #                                radius)
        return self._draw3dmol_cylinder(color, center,
                                        np.array(center) + np.array(normal) * 0.01,
                                        True, True,
                                        opacity,
                                        radius, clickable, batch)

    def draw_cylinder(self, start, end, radius,
                      color='red', opacity=1.0, clickable=False,
                      batch=False):
        return self._draw3dmol_cylinder(color, start,
                                        end,
                                        True, True,
                                        opacity,
                                        radius, clickable, batch)

    def draw_tube(self, start, end, radius,
                  color='red', opacity=1.0, clickable=False,
                  batch=False):
        return self._draw3dmol_cylinder(color, start,
                                        end,
                                        False, False,
                                        opacity,
                                        radius, clickable, batch)

    def _draw3dmol_cylinder(self, color, start, end,
                            draw_start_face, draw_end_face,
                            opacity, radius, clickable, batch):
        color = translate_color(color)
        js_shape = JSObject('shape')
        facestart = self._convert_units(start)
        faceend = self._convert_units(end)
        radius = self._convert_units(radius)
        spec = dict(
                start=self._list_to_jsvec(facestart),
                end=self._list_to_jsvec(faceend),
                radius=radius,
                color=color,
                alpha=opacity,
                fromCap=draw_start_face, toCap=draw_end_face)
        args = ['Cylinder', spec, js_shape.id, clickable]
        if batch:
            self.batch_message('renderPyShape', args)
        else:
            self.viewer('renderPyShape', args)
        return js_shape

    def draw_arrow(self, start, end=None, vector=None,
                   radius=0.15, color='red',
                   opacity=1.0, clickable=False):
        if (end is None) == (vector is None):
            raise ValueError("Either 'end' or 'vector' should be passed, but not both.")
        if end is None: end = np.array(start) + np.array(vector)
        facestart = self._convert_units(start)
        faceend = self._convert_units(end)
        color = translate_color(color)

        spec = dict(
                start=self._list_to_jsvec(facestart),
                end=self._list_to_jsvec(faceend),
                radius=radius,
                color=color,
                alpha=opacity)
        js_shape = JSObject('shape')
        self.viewer('renderPyShape', ['Arrow',
                                      spec,
                                      js_shape.id,
                                      clickable])
        return js_shape

    def remove_all_shapes(self):
        self.viewer('removeAllShapes', [])

    def remove(self, obj, batch=False):
        if batch: viewer_call = self.batch_message
        else: viewer_call = self.viewer
        if obj.type == 'shape':
            viewer_call('removePyShape', [obj.id])
        elif obj.type == 'label':
            viewer_call('removePyLabel', [obj.id])
        else:
            raise ValueError('Unknown object type %s' % obj.type)

    # Labels
    def draw_label(self, position, text,
                   background='black',
                   border='black',
                   color='white',
                   fontsize=14, opacity=1.0):
        js_label = JSObject('label')
        position = self._convert_units(position)
        color = translate_color(color)
        background = translate_color(background)
        spec = dict(position=self._list_to_jsvec(position),
                    fontColor=color,
                    backgroundColor=background,
                    borderColor=border,
                    fontSize=fontsize,
                    backgroundOpacity=opacity)
        self.viewer('renderPyLabel', [text, spec, js_label.id])
        return js_label

    def remove_all_labels(self):
        self.viewer('removeAllLabels', [])

    def get_voldata(self, orbname, npts, framenum):
        orbital_key = (orbname, npts, framenum)
        if orbital_key not in self._cached_voldata:
            grid = self.calc_orb_grid(orbname, npts, framenum)
            self.cache_grid(grid, orbname, npts, framenum)
        return self._cached_voldata[orbital_key]

    def cache_grid(self, grid, orbname, npts, framenum):
        orbital_key = (orbname, npts, framenum)
        cubefile = self._grid_to_cube(grid)
        volume_data = self.read_cubefile(cubefile)
        self._cached_voldata[orbital_key] = volume_data

    def draw_orbital(self, orbname, npts=50, isoval=0.01,
                     opacity=0.8,
                     negative_color='red',
                     positive_color='blue',
                     remove_old_orbitals=True):
        """Display a molecular orbital

        Args:
            orbname: name of the orbital (interface dependent)
            npts (int): resolution in each dimension
            isoval (float): isosurface value to draw
            opacity (float): opacity of the orbital (between 0 and 1)
            positive_color (str or int): color of the positive isosurfaces
            negative_color (str or int): color of the negative isosurfaces
            remove_old_orbitals (bool): remove any previously drawn orbitals
        """
        self.orbital_spec = dict(npts=npts, isoval=isoval,
                                 opacity=opacity,
                                 negative_color=negative_color,
                                 positive_color=positive_color)
        self.current_orbital = orbname

        if remove_old_orbitals:
            self.remove_orbitals()

        positive_color = translate_color(positive_color)
        negative_color = translate_color(negative_color)

        orbidx = self.get_orbidx(orbname)
        voldata = self.get_voldata(orbidx, npts, self.current_frame)
        positive_orbital = JSObject('shape')
        self.viewer('drawIsosurface',
                    [voldata.id,
                     positive_orbital.id,
                     {'isoval': isoval,
                      'color': positive_color,
                      'opacity': opacity}])
        negative_orbital = JSObject('shape')
        self.viewer('drawIsosurface',
                    [voldata.id,
                     negative_orbital.id,
                     {'isoval': -isoval,
                      'color': negative_color,
                      'opacity': opacity}])
        self.current_js_orbitals.extend([positive_orbital, negative_orbital])

    def remove_orbitals(self):
        if self.current_js_orbitals:
            for orbital in self.current_js_orbitals:
                self.remove(orbital)
            self.current_js_orbitals = []

    def get_orbidx(self, orbname):
        try:
            if orbname.lower().strip() == 'homo':
                orbname = self.homo_index()
            elif orbname.lower().strip() == 'lumo':
                orbname = self.homo_index() + 1
        except AttributeError:
            pass
        return orbname

    def get_orbnames(self):
        raise NotImplementedError

    def read_cubefile(self, cubefile):
        volume_data = JSObject('shape')
        self.viewer('processCubeFile', [cubefile, volume_data.id])
        return volume_data

    @staticmethod
    def _grid_to_cube(grid,f=None):
        if f is None:
            fobj = StringIO()
        elif not hasattr(f,'write'):
            fobj = open(f,'w')
        else:
            fobj = f

        # First two header lines
        print>> fobj, 'CUBE File\nGenerated by nbmolviz'
        # third line: number of atoms (0, here) + origin of grid
        print>> fobj, '-1 %f %f %f' % grid.origin()
        # lines 4-7: number of points in each direction and basis vector for each
        # basis vectors are negative to indicate angstroms
        print >> fobj, '%d %f 0.0 0.0' % (-grid.npoints, grid.dx)
        print >> fobj, '%d 0.0 %f 0.0' % (-grid.npoints, grid.dy)
        print >> fobj, '%d 0.0 0.0 %f' % (-grid.npoints, grid.dz)
        # Next is a line per atom
        # We put just one atom here - it shouldn't be rendered
        print >> fobj, '6 0.000 0.0 0.0 0.0'
        # Next, indicate that there's just one orbital
        print >> fobj, 1, 1
        # finally, write out all the grid values
        # ival = 0
        for ix in xrange(grid.npoints):
            for iy in xrange(grid.npoints):
                for iz in xrange(grid.npoints):
                    print >> fobj, grid.fxyz[ix, iy, iz],
                    # ival += 1
                    # if ival%6 == 0: print >> fobj #newline
                    if iz % 6 == 5: print >> fobj
                print >> fobj

        if f is None:
            fobj.seek(0)
            return fobj.getvalue()
        else:
            fobj.close()


