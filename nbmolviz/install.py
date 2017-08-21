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
import os
import sys
import collections
import subprocess

import nbmolviz

PKGPATH = nbmolviz.__path__[0]

EXTENSION_KWARGS = {'user': {'user':True},
                    'system': {},
                    'environment': {'sys_prefix':True},}


NbExtVersion = collections.namedtuple('NbExtVersion', 'name installed path version'.split())


def nbextension_ordered_paths():
    import jupyter_core.paths as jupypaths
    jupyter_searchpath = jupypaths.jupyter_path()

    paths = [('user', jupypaths.jupyter_data_dir()),
             ('environment', jupypaths.ENV_JUPYTER_PATH[0]),
             ('system', jupypaths.SYSTEM_JUPYTER_PATH[0])]

    paths.sort(key=lambda x: jupyter_searchpath.index(x[1]))
    return collections.OrderedDict(paths)


def get_installed_versions(extname, getversion):
    """ Check if the required NBExtensions are installed. If not, prompt user for action.
    """
    from notebook import nbextensions

    search_paths = nbextension_ordered_paths()

    installed = {k: nbextensions.check_nbextension(extname, **EXTENSION_KWARGS[k])
                 for k in search_paths.keys()}

    paths = {}
    versions = {}
    for k in EXTENSION_KWARGS:
        if not installed[k]:
            continue

        paths[k] = os.path.join(search_paths[k], 'nbextensions', extname)

        if getversion:
            versionfile = os.path.join(paths[k], 'VERSION')
            if installed[k] and os.path.exists(versionfile):
                with open(versionfile, 'r') as pfile:
                    versions[k] = pfile.read().strip()
            else:
                versions[k] = 'pre-0.7'

    return {k: NbExtVersion(extname, installed[k], paths.get(k, None), versions.get(k, None))
            for k in installed}


def activate(flags):
    try:
        activate_extension('widgetsnbextension', flags)
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 2:
            raise PermissionError(
                    ('ERROR - failed to enable the widget extensions with %s.' % flags) +
                  ' Try rerunning the command with \"sudo\"!')
        else:
            raise

    activate_extension('nbmolviz', flags)


def activate_extension(pyname, flags):
    _jnbextrun('install', pyname, flags)
    _jnbextrun('enable', pyname, flags)


def uninstall(flags):
    try:
        deactivate_extension('nbmolviz', flags)
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 2:
            raise PermissionError(
                    ('ERROR - failed to uninstall the widget extensions with %s.' % flags) +
                    ' Try rerunning the command with \"sudo\"!')
        sys.exit(2)


def deactivate_extension(pyname, flags):
    _jnbextrun('disable', pyname, flags)
    _jnbextrun('uninstall', pyname, flags)


def _jnbextrun(cmd, lib, flags):
    shellcmd = ['jupyter', 'nbextension', cmd, '--py', flags, lib]
    print('> %s' % ' '.join(shellcmd))
    subprocess.check_call(shellcmd)
    return shellcmd


def find_nbmolviz_extension(extname):
    import jupyter_core.paths as jupypaths
    for extpath in jupypaths.jupyter_path('nbextensions'):
        mypath = os.path.join(extpath, extname)
        if os.path.lexists(mypath):
            return extpath
    else:
        return None
