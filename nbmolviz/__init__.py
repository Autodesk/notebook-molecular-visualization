from nbmolviz import utils
from nbmolviz import base_widget,widget3d,interfaces3d,drivers3d,widget2d

backend = '3dmol.js' #default
_BACKENDS = {'3dmol.js': drivers3d.MolViz_3DMol}
_INTERFACES = {}


def _set_up_interfaces():
    try: import MDAnalysis as mda
    except ImportError: pass
    else: _INTERFACES[mda.Universe] = interfaces3d.MdaViz

    try: import pybel as pb
    except ImportError: pass
    else: _INTERFACES[pb.Molecule] = interfaces3d.PybelViz

    try: import cclib.parser.data
    except ImportError: pass
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


def visualize(mol,format=None,**kwargs):
    mytype = type(mol)

    if mytype == str:
        #deal with strings as input
        import pybel as pb
        if len(mol)>40: #assume it's the content of a file
            if format is None: format = 'pdb'
            mol = pb.readstring(format,mol).next()
        else:
            if format is None: format = mol.split('.')[-1]
            mol = pb.readfile(format,mol).next()
        mytype = type(mol)

    #Create an appropriate class
    class BespokeVisualizer(_BACKENDS[backend], _INTERFACES[mytype]): pass
    return BespokeVisualizer(mol,**kwargs)
