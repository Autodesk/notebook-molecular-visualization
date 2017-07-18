from __future__ import division
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
from builtins import zip
from builtins import str
from past.builtins import basestring
from past.utils import old_div
from builtins import object
import uuid

import webcolors


def make_layout(layout=None, **kwargs):
    from ipywidgets import Layout
    import traitlets

    if layout is None:
        layout = Layout()
    for key, val in kwargs.items():
        # note that this is the type of the class descriptor, not the instance attribute
        if isinstance(getattr(Layout, key), traitlets.Unicode):
            val = in_pixels(val)
        setattr(layout, key, val)
    return layout


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

    if isinstance(color, basestring):
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


def in_pixels(x):
    if isinstance(x, basestring):
        return x
    else:
        return str(x) + 'px'


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
        newnumber = int( old_div(float(self.number), other))
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