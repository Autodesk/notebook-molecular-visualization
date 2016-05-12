import os
from notebook.nbextensions import install_nbextension
import nbmolviz

PKGPATH = nbmolviz.__path__[0]


def widgets(overwrite=True):
    """Install the widgets. This isn't actually used, for now - we just load them
    the nbmolviz directory"""
    install_nbextension(os.path.join(PKGPATH, 'static'),
                        destination='molviz',
                        overwrite=overwrite)

def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="nbmolvizjs",
        # _also_ in the `nbextension/` namespace
        require="my_fancy_module/index")]


if __name__ == '__main__':
    widgets()
