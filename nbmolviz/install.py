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
import collections

import nbmolviz

PKGPATH = nbmolviz.__path__[0]


EXTENSION_KWARGS = {'user': {'user':True},
                    'system': {},
                    'environment': {'sys_prefix':True}}


NbExtVersion = collections.namedtuple('NbExtVersion', 'name installed path version'.split())


def nbextension_check(extname, getversion):
    """ Check if the required NBExtensions are installed. If not, prompt user for action.
    """
    import jupyter_core.paths as jupypaths
    from notebook import nbextensions

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

    installed = {k: nbextensions.check_nbextension('nbmolviz-js', **kwargs) for k,kwargs in EXTENSION_KWARGS.items()}
    jupyter_dir = {'user': jupypaths.jupyter_data_dir(),
                   'environment': jupypaths.ENV_JUPYTER_PATH[0],
                   'system': jupypaths.SYSTEM_JUPYTER_PATH[0]}
    paths = {}
    versions = {}
    for k in EXTENSION_KWARGS:
        if not installed[k]:
            continue

        paths[k] = os.path.join(jupyter_dir[k], 'nbextensions', extname)

        if getversion:
            versionfile = os.path.join(paths[k], 'VERSION')
            if installed[k] and os.path.exists(versionfile):
                with open(versionfile, 'r') as pfile:
                    versions[k] = pfile.read().strip()
            else:
                versions[k] = 'pre-0.8'

    return {k: NbExtVersion(extname, installed[k], paths.get(k, None), versions.get(k, None))
            for k in installed}


def find_nbmolviz_extension(extname):
    import jupyter_core.paths as jupypaths
    for extpath in jupypaths.jupyter_path('nbextensions'):
        mypath = os.path.join(extpath, extname)
        if os.path.lexists(mypath):
            return extpath
    else:
        return None

