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
import numpy as np

import webcolors

ANGSTROM_PER_BOHR = 0.5291772616368011
BOHR_PER_ANGSTROM = 1.8897259434513847

atomic_numbers = {'Ac': 89, 'Ag': 47, 'Al': 13, 'Am': 95, 'Ar': 18, 'As': 33, 'At': 85, 'Au': 79,
                  'B': 5, 'Ba': 56, 'Be': 4, 'Bh': 107, 'Bi': 83, 'Bk': 97, 'Br': 35, 'C': 6,
                  'Ca': 20, 'Cd': 48, 'Ce': 58, 'Cf': 98, 'Cl': 17, 'Cm': 96, 'Cn': 112, 'Co': 27,
                  'Cr': 24, 'Cs': 55, 'Cu': 29, 'Db': 105, 'Ds': 110, 'Dy': 66, 'Er': 68, 'Es': 99,
                  'Eu': 63, 'F': 9, 'Fe': 26, 'Fm': 100, 'Fr': 87, 'Ga': 31, 'Gd': 64, 'Ge': 32,
                  'H': 1, 'He': 2, 'Hf': 72, 'Hg': 80, 'Ho': 67, 'Hs': 108, 'I': 53, 'In': 49, 'Ir': 77,
                  'K': 19, 'Kr': 36, 'La': 57, 'Li': 3, 'Lr': 103, 'Lu': 71, 'Md': 101, 'Mg': 12,
                  'Mn': 25, 'Mo': 42, 'Mt': 109, 'N': 7, 'Na': 11, 'Nb': 41, 'Nd': 60, 'Ne': 10,
                  'Ni': 28, 'No': 102, 'Np': 93, 'O': 8, 'Os': 76, 'P': 15, 'Pa': 91, 'Pb': 82,
                  'Pd': 46, 'Pm': 61, 'Po': 84, 'Pr': 59, 'Pt': 78, 'Pu': 94, 'Ra': 88, 'Rb': 37,
                  'Re': 75, 'Rf': 104, 'Rg': 111, 'Rh': 45, 'Rn': 86, 'Ru': 44, 'S': 16, 'Sb': 51,
                  'Sc': 21, 'Se': 34, 'Sg': 106, 'Si': 14, 'Sm': 62, 'Sn': 50, 'Sr': 38, 'Ta': 73,
                  'Tb': 65, 'Tc': 43, 'Te': 52, 'Th': 90, 'Ti': 22, 'Tl': 81, 'Tm': 69, 'U': 92,
                  'Uuh': 116, 'Uuo': 118, 'Uup': 115, 'Uuq': 114, 'Uus': 117, 'Uut': 113, 'V': 23,
                  'W': 74, 'Xe': 54, 'Y': 39, 'Yb': 70, 'Zn': 30, 'Zr': 40}

elements = {atnum:el for el,atnum in atomic_numbers.iteritems()}


def translate_color(color, prefix='0x'):
    """ Return a normalized for a given color, specified as hex or as a CSS3 color name.

    Args:
        color (int or str): can be an integer, hex code (with or without '0x' or '#'), or
            css3 color name
        prefix (str): prepend the raw hex string with this (usually '#' or '0x')

    Returns:
        str: hex string of the form '0x123abc'
    """
    formatter = prefix + '{:06x}'

    if issubclass(type(color), basestring):
        if color.lower() in webcolors.css3_names_to_hex:
            color = webcolors.css3_names_to_hex[color.lower()]

        if len(color) == 7 and color[0] == '#':  # hex that starts with '#'
            color = color[1:]
        elif len(color) == 8 and color[0:2] == '0x':  # hex str that starts with '0x'
            color = color[2:]

        if len(color) == 6:  # hex without prefix
            color = prefix + color
        else:
            raise ValueError('Failed to translate color %s' % color)

    elif isinstance(color, int):
        color = formatter.format(color)

    else:
        raise ValueError('Unrecognized color %s of type %s' % (color, type(color)))

    return color


class JSObject(object):
    """This is a convenient python reference to a javascript object.
    Really, it just stores a string"""

    def __init__(self, type, objid=None):
        self.type = type
        if objid is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = objid

    def __eq__(self, other):
        if hasattr(other, 'id'):
            return self.id == other.id
        else:
            return self.id == other

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.id)


def bbox(coords, padding=5., BIG=1e12):
    """Return a bounding box for a molecule.
    Derived from pyquante2.geo.molecule.bbox"""
    xmin = ymin = zmin = BIG
    xmax = ymax = zmax = -BIG
    for x, y, z in coords:
        xmin = min(x, xmin)
        ymin = min(y, ymin)
        zmin = min(z, zmin)
        xmax = max(x, xmax)
        ymax = max(y, ymax)
        zmax = max(z, zmax)
    xmin, ymin, zmin = xmin - padding, ymin-padding, zmin-padding
    xmax, ymax, zmax = xmax+padding, ymax+padding, zmax+padding
    return xmin, xmax, ymin, ymax, zmin, zmax


class VolumetricGrid(object):
    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax,
                 npoints=None):
        self.xr = (xmin, xmax)
        self.yr = (ymin, ymax)
        self.zr = (zmin, zmax)
        if npoints is not None:
            self.make_grid(npoints)

    def xyzlist(self):
        stride = self.npoints*1j
        grids = np.mgrid[self.xr[0]:self.xr[1]:stride,
                        self.yr[0]:self.yr[1]:stride,
                        self.zr[0]:self.zr[1]:stride]
        return grids

    def origin(self):
        return (self.xr[0],self.yr[0],self.zr[0])

    def make_grid(self,npoints):
        self.npoints = npoints
        self.fxyz = np.zeros((npoints,npoints,npoints))
        self.dx = (self.xr[1]-self.xr[0]) / (float(npoints)-1)
        self.dy = (self.yr[1]-self.yr[0]) / (float(npoints)-1)
        self.dz = (self.zr[1]-self.zr[0]) / (float(npoints)-1)

try:
    import pyquante2
except ImportError:
    pass
else:
    class CCLibBasis(pyquante2.basisset):
        """Edited version of the superclass __init__ that supports cclib gbasis
        """
        def __init__(self,gbasis,coords):
            from pyquante2.basis.tools import sym2pow,sym2am,am2pow,am2sym
            self.bfs = []
            self.shells = []
            for atom_basis_function,pos in zip(gbasis,coords):
                for sym,prims in atom_basis_function:
                    exps = [e for e,c in prims]
                    coefs = [c for e,c in prims]
                    self.shells.append(
                        pyquante2.basis.basisset.shell(sym2am[sym],
                                              pos*BOHR_PER_ANGSTROM,
                                              exps,coefs))
                    for power in sym2pow[sym]:
                        self.bfs.append(
                            pyquante2.basis.cgbf.cgbf(
                                pos*BOHR_PER_ANGSTROM,
                                power,exps,coefs))


def calc_orbvals(grid,orb,bfs):
    """Derived from pyquante2.graphics.mayavi.vieworb"""
    x, y, z = grid.xyzlist()
    for c,bf in zip(orb,bfs):
        grid.fxyz += c*bf(x*BOHR_PER_ANGSTROM,
                          y*BOHR_PER_ANGSTROM,
                          z*BOHR_PER_ANGSTROM)
    return grid


class Measure(object):
    def __init__(self,pxstr):
        if type(pxstr) in (int,float):
            self.number = int(pxstr)
            self.unit = 'px'
        else:
            self.number = int( ''.join(c for c in pxstr if c.isdigit()))
            self.unit = ''.join(c for c in pxstr if not c.isdigit())
            if self.unit.strip() == '': self.unit='px' #guess pixels

    def __str__(self):
        return '%d%s'%(self.number,self.unit)

    def __repr__(self):
        return '<Measure:%s>'%str(self)

    def __mul__(self,other):
        newnumber = int( float(self.number) * other)
        return Measure('%d%s'%(newnumber,self.unit) )

    __rmul__ = __mul__

    def __div__(self,other):
        newnumber = int( float(self.number) / other)
        return Measure( '%d%s'%(newnumber,self.unit))


BENZENE_SDF = """241
  -OEChem-11131519563D

 12 12  0     0  0  0  0  0  0999 V2000
   -1.2131   -0.6884    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2028    0.7064    0.0001 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.0103   -1.3948    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0104    1.3948   -0.0001 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2028   -0.7063    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2131    0.6884    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -2.1577   -1.2244    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -2.1393    1.2564    0.0001 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.0184   -2.4809   -0.0001 H   0  0  0  0  0  0  0  0  0  0  0  0
    0.0184    2.4808    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    2.1394   -1.2563    0.0001 H   0  0  0  0  0  0  0  0  0  0  0  0
    2.1577    1.2245    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0  0  0  0
  1  3  1  0  0  0  0
  1  7  1  0  0  0  0
  2  4  1  0  0  0  0
  2  8  1  0  0  0  0
  3  5  2  0  0  0  0
  3  9  1  0  0  0  0
  4  6  2  0  0  0  0
  4 10  1  0  0  0  0
  5  6  1  0  0  0  0
  5 11  1  0  0  0  0
  6 12  1  0  0  0  0
M  END
> <PUBCHEM_COMPOUND_CID>
241

> <PUBCHEM_CONFORMER_RMSD>
0.4

> <PUBCHEM_CONFORMER_DIVERSEORDER>
1

> <PUBCHEM_MMFF94_PARTIAL_CHARGES>
12
1 -0.15
10 0.15
11 0.15
12 0.15
2 -0.15
3 -0.15
4 -0.15
5 -0.15
6 -0.15
7 0.15
8 0.15
9 0.15

> <PUBCHEM_EFFECTIVE_ROTOR_COUNT>
0

> <PUBCHEM_PHARMACOPHORE_FEATURES>
1
6 1 2 3 4 5 6 rings

> <PUBCHEM_HEAVY_ATOM_COUNT>
6

> <PUBCHEM_ATOM_DEF_STEREO_COUNT>
0

> <PUBCHEM_ATOM_UDEF_STEREO_COUNT>
0

> <PUBCHEM_BOND_DEF_STEREO_COUNT>
0

> <PUBCHEM_BOND_UDEF_STEREO_COUNT>
0

> <PUBCHEM_ISOTOPIC_ATOM_COUNT>
0

> <PUBCHEM_COMPONENT_COUNT>
1

> <PUBCHEM_CACTVS_TAUTO_COUNT>
1

> <PUBCHEM_CONFORMER_ID>
000000F100000001

> <PUBCHEM_MMFF94_ENERGY>
13.148

> <PUBCHEM_FEATURE_SELFOVERLAP>
5.074

> <PUBCHEM_SHAPE_FINGERPRINT>
16714656 1 18123201108121732318
20096714 4 18339082562313515547
21015797 1 9222644709913001990
21040471 1 18194402190896164549

> <PUBCHEM_SHAPE_MULTIPOLES>
123.48
1.59
1.59
0.62
0
0
0
0
0
0
0
0
0
0

> <PUBCHEM_SHAPE_SELFOVERLAP>
251.998

> <PUBCHEM_SHAPE_VOLUME>
67.5

> <PUBCHEM_COORDINATE_TYPE>
2
5
10

$$$$"""