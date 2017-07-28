from __future__ import print_function, absolute_import, division
from builtins import map
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

from moldesign import units as u

import numpy as np
import collections
import webcolors

DEF_CATEGORICAL = 'Paired'
DEF_SEQUENTIAL = None  # should be inferno, but that's only MPL >1.5


def colormap(cats, mplmap='auto', categorical=None):
    """ Map a series of categories to hex colors, using a matplotlib colormap

    Generates both categorical and numerical colormaps.

    Args:
        cats (Iterable): list of categories or numerical values
        mplmap (str): name of matplotlib colormap object
        categorical (bool): If None
            (the default) interpret data as numerical only if it can be cast to float.
            If True, interpret this data as categorical. If False, cast the data to float.

    Returns:
        List[str]: List of hexadecimal RGB color values in the in the form ``'#000102'``
    """
    # Should automatically choose the right colormaps for:
    #  categorical data
    #  sequential data (low, high important)
    #  diverging data (low, mid, high important)
    global DEF_SEQUENTIAL
    from matplotlib import cm

    if hasattr(cm, 'inferno'):
        DEF_SEQUENTIAL = 'inferno'
    else:
        DEF_SEQUENTIAL = 'BrBG'

    # strip units
    units = None  # TODO: build a color bar with units
    if hasattr(cats[0], 'magnitude'):
        arr = u.array(cats)
        units = arr.units
        cats = arr.magnitude
        is_categorical = False
    else:
        is_categorical = not isinstance(cats[0], (float, int))

    if categorical is not None:
        is_categorical = categorical

    if is_categorical:
        values = _map_categories_to_ints(cats)
        if mplmap == 'auto':
            mplmap = DEF_CATEGORICAL
    else:
        values = np.array(list(map(float, cats)))
        if mplmap == 'auto':
            mplmap = DEF_SEQUENTIAL

    rgb = _cmap_to_rgb(mplmap, values)
    hexcolors = [webcolors.rgb_to_hex(np.array(c)) for c in rgb]
    return hexcolors


def _map_categories_to_ints(cats):
    values = np.zeros(len(cats), dtype='float')
    to_int = collections.OrderedDict()
    for i, item in enumerate(cats):
        if item not in to_int:
            to_int[item] = len(to_int)
        values[i] = to_int[item]
    return values


def _cmap_to_rgb(mplmap, values):
    from matplotlib import cm

    cmap = getattr(cm, mplmap)
    mx = values.max()
    mn = values.min()
    cat_values = (values-mn)/(mx-mn)  # rescale values [0.0,1.0]
    rgba = cmap(cat_values)  # array of RGBA values in range [0.0, 1.0]

    # strip alpha field and rescale to [0,255] RGB integers
    rgb = [list(map(int, c[:3]*256.0)) for c in rgba]
    return rgb


def is_color(s):
    """ Do our best to determine if "s" is a color spec that can be converted to hex

    Args:
        s (str or int): string or integer describing a color

    Returns:
        bool: True if this can be converted to a hex-compatible color
    """
    def in_range(i): return 0 <= i <= int('0xFFFFFF', 0)

    try:
        if type(s) == int:
            return in_range(s)
        elif type(s) not in (str, bytes):
            return False
        elif s in webcolors.css3_names_to_hex:
            return True
        elif s[0] == '#':
            return in_range(int('0x' + s[1:], 0))
        elif s[0:2] == '0x':
            return in_range(int(s, 0))
        elif len(s) == 6:
            return in_range(int('0x' + s, 0))
    except ValueError:
        return False
