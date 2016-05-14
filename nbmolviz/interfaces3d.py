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
import collections

from nbmolviz.widget3d import MolViz3DBaseWidget
from nbmolviz import utils


class AlwaysBenzene(MolViz3DBaseWidget):
    "It's always benzene"
    def __init__(self,**kwargs):
        super(AlwaysBenzene,self).__init__(mol='dummy',**kwargs)

    "fixed to benzene without any interface"
    def get_input_file(self):
        return utils.BENZENE_SDF,'sdf'

    @staticmethod
    def _atoms_to_json(atoms):
        return {'index': [i for i in atoms]}

    def make_animation(self):
        "Let's do a nuclear fusion breathing mode for debugging purposes ..."
        coords = np.array([[  -1.2131 ,  -0.6884  ,  0.0000 ],
                           [ -1.2028  ,  0.7064  ,  0.0001 ],
                           [ -0.0103  , -1.3948  ,  0.0000 ],
                           [  0.0104  ,  1.3948 ,  -0.0001 ],
                           [ 1.2028 ,  -0.7063  ,  0.0000 ],
                           [    1.2131 ,   0.6884  ,  0.0000],
                           [   -2.1577 ,  -1.2244  ,  0.0000 ],
                           [   -2.1393 ,   1.2564  ,  0.0001 ],
                           [   -0.0184 ,  -2.4809  , -0.0001 ],
                           [    0.0184 ,   2.4808  ,  0.0000 ],
                           [    2.1394 ,  -1.2563  ,  0.0001 ],
                           [    2.1577 ,   1.2245  ,  0.0000 ]])
        for i in xrange(40):
            scalefac = np.sin(i/15.0)
            self.append_frame(coords * scalefac)
        self.frames_ready = True

class PybelViz(MolViz3DBaseWidget):
    """Visualize a pybel molecule"""
    @staticmethod
    def _atoms_to_json(atomlist):
        idxes = [a.idx for a in atomlist]
        atomsel = {'serial':idxes.tolist()}
        return atomsel

    def get_input_file(self):
        instring = self.mol.write('sdf')
        return instring,'sdf'


class MdaViz(MolViz3DBaseWidget):
    """Visualize an MDAnalysis molecule"""
    def __init__(self,*args,**kwargs):
        super(MdaViz,self).__init__(*args,**kwargs)
        self.frame_map = {}
        self.frames_ready = False

    @staticmethod
    def _atoms_to_json(atomgroup):
        atomsel = {'serial':(atomgroup.indices+1).tolist()}
        return atomsel

    def get_positions(self):
        return self.mol.atoms.positions

    def get_input_file(self):
        """TODO:don't use a temporary file!"""
        fname ='/tmp/temp%s.pdb'%self.viewerId
        self.mol.atoms.write(fname)
        with open(fname,'r') as infile:
            molstring = infile.read()
        return molstring,'pdb'

    def make_animation(self):
        traj = self.mol.universe.trajectory
        traj.rewind()
        for iframe,frame in enumerate(traj):
            framenum = self.append_frame()
            self.frame_map[iframe] = framenum
        self.frames_ready = True


class CCLibViz(MolViz3DBaseWidget):
    """
    TODO: cclib doesn't return the name of the basis, just the parameters if it can find them. If we can figure out that we're using, e.g., 6-31g**, we should be able to reconstruct that ourselves?
    """
    def __init__(self,*args,**kwargs):
        super(CCLibViz,self).__init__(*args,**kwargs)
        self.basis = self.build_basis()

    def build_basis(self):
        """TODO: deal with multiple coordinates and orbitals. For now, take the last one of each
        TODO: lose the pyquante dependency?"""
        gbasis = self.mol.gbasis
        coords = self.mol.atomcoords[-1]
        assert len(self.mol.atomnos) == len(gbasis)
        self.bfs = utils.CCLibBasis(gbasis,coords)

    def get_input_file(self):
        coords = self.mol.atomcoords[-1]
        outfile = [' %d \ncomment line' % len(coords)]
        for atnum, pos in zip(self.mol.atomnos, coords):
            outfile.append('%s %f %f %f' % (utils.elements[atnum],
                                            pos[0], pos[1], pos[2]))
        return '\n'.join(outfile), 'xyz'

    def calc_orb_grid(self, orbnum, npts=50):
        bbox = utils.bbox(self.mol.atomcoords[-1])
        grid = utils.VolumetricGrid(*bbox, npoints=npts)
        orb = self.mol.mocoeffs[-1][:, orbnum]
        return utils.calc_orbvals(grid, orb, self.bfs)

    def get_orbnames(self):
        orbnames = collections.OrderedDict()
        for i in xrange(self.mol.nbasis): orbnames[str(i)] = i
        return orbnames

    @property
    def homo(self):
        return self.mol.homos[-1]


class PyQuante2Viz(MolViz3DBaseWidget):
    """This takes a pyquante2 solver """

    def __init__(self, *args, **kwargs):
        super(PyQuante2Viz, self).__init__(*args, **kwargs)
        if kwargs.get('display', True):  # because we don't get bonds by default (?)
            self.set_style('sphere', radius=0.3)

    def get_input_file(self):
        from cStringIO import StringIO
        fobj = StringIO()
        self.mol.geo.xyz(fobj=fobj)
        xyzfile = fobj.getvalue()
        fobj.close()
        try:  # use pybel to assign bonds if available
            import pybel as pb
        except ImportError:
            return xyzfile, 'xyz'
        else:
            pbmol = pb.readstring('xyz', xyzfile)
            sdffile = pbmol.write('sdf')
            return sdffile,'sdf'

    def calc_orb_grid(self,orbnum,npts=50):
        grid = utils.VolumetricGrid( *self.mol.geo.bbox(),
                                      npoints=npts)
        orb = self.mol.orbs[:,orbnum]
        return utils.calc_orbvals(grid,orb,self.mol.bfs)

    def get_orbnames(self):
        orbnames = collections.OrderedDict()
        for i in xrange( len(self.mol.bfs) ): orbnames[str(i)] = i
        return orbnames

    @property
    def homo(self):
        return self.mol.geo.nel()/2 - 1


