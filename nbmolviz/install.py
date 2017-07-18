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
import sys
import os
from notebook.nbextensions import install_nbextension
import nbmolviz

PKGPATH = nbmolviz.__path__[0]

def nbextension_check():
    """ Check if the required NBExtensions are installed. If not, prompt user for action.
    """
    # TODO: implement the following:
    # 0. Resolve jupyter nbextension search path, find installed
    #    jupyter-js-widgets and nbmolviz-js extensions and their versions
    # 1. If extension with correct version is installed and enabled, do nothing, we're done
    # 2. If correct extensions are installed but not enabled, prompt user to enable
    # 3. If there are multiple copies, and the wrong version(s) are enabled, prompt user to
    #       enable the right ones
    # 4. If not installed, prompt user to install/enable in the first writeable instance of
    #       the following: sys-prefix, user-dir, systemwide

    # see https://github.com/ipython-contrib/jupyter_contrib_nbextensions/blob/master/src/jupyter_contrib_nbextensions/install.py


def in_virtualenv():
    """
    See https://stackoverflow.com/a/1883251/1958900
    """
    if hasattr(sys, 'real_prefix') or hasattr(sys, 'base_prefix'):
        return True
    else:
        return False


def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="nbmolvizjs",
        # _also_ in the `nbextension/` namespace
        require="my_fancy_module/index")]

