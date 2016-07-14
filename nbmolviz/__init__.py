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
import os as _os


from nbmolviz import utils
from nbmolviz import base_widget, widget3d, interfaces3d, drivers3d, widget2d

# package metadata
from nbmolviz import _version
__version__ = _version.get_versions()['version']
__copyright__ = "Copyright 2016 Autodesk Inc."
__license__ = "Apache 2.0"

PACKAGE_PATH = _os.path.dirname(_os.path.abspath(__file__))

backend = '3dmol.js'  # default
_BACKENDS = {'3dmol.js': drivers3d.MolViz_3DMol}
_INTERFACES = {}


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'nbmolviz-js',
        'require': 'nbmolviz-js/extension'
    }]

# TODO: all code below shouldn't be in __init__.py


def find_static_assets():
    from warnings import warn
    warn("""To use the nbmolviz-js nbextension, you'll need to update
    the Jupyter notebook to version 4.2 or later.""")
    return []


def _set_up_interfaces():
    try:
        import MDAnalysis as mda
    except ImportError:
        pass
    else:
        _INTERFACES[mda.Universe] = interfaces3d.MdaViz

    try:
        import pybel as pb
    except ImportError:
        pass
    else:
        _INTERFACES[pb.Molecule] = interfaces3d.PybelViz

    try:
        import cclib.parser.data
    except ImportError:
        pass
    else:
        _INTERFACES[cclib.parser.data.ccData_optdone_bool] = interfaces3d.CCLibViz
        _INTERFACES[cclib.parser.data.ccData] = interfaces3d.CCLibViz


_set_up_interfaces()


def test3d(driver=None):
    """Construct a view of benzene"""
    if driver is None:
        driver = backend

    class NewClass(interfaces3d.AlwaysBenzene, _BACKENDS[driver]):
        pass

    view = NewClass()
    return view


def visualize(mol, format=None, **kwargs):
    mytype = type(mol)

    if mytype == str:
        # deal with strings as input
        import pybel as pb
        if len(mol) > 40:  # assume it's the content of a file
            if format is None: format = 'pdb'
            mol = pb.readstring(format, mol).next()
        else:
            if format is None: format = mol.split('.')[-1]
            mol = pb.readfile(format, mol).next()
        mytype = type(mol)

    # Create an appropriate class
    class BespokeVisualizer(_BACKENDS[backend], _INTERFACES[mytype]):
        pass

    return BespokeVisualizer(mol, **kwargs)
