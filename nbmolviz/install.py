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

FLAGS = {'environment': '--sys-prefix',
         'system': '--system',
         'user': '--user'}

NbExtVersion = collections.namedtuple(
        'NbExtVersion', 'name installed path version enabled active writable'.split())


def nbextension_ordered_paths():
    import jupyter_core.paths as jupypaths
    jupyter_searchpath = jupypaths.jupyter_path()

    paths = [('user', jupypaths.jupyter_data_dir()),
             ('environment', jupypaths.ENV_JUPYTER_PATH[0]),
             ('system', jupypaths.SYSTEM_JUPYTER_PATH[0])]

    paths.sort(key=lambda x: jupyter_searchpath.index(x[1]))
    return collections.OrderedDict(paths)


def jupyter_config_dirs():
    import jupyter_core.paths as jupypaths
    cdirs = {'user': jupypaths.jupyter_config_dir(),
             'environment': jupypaths.ENV_CONFIG_PATH[0],
             'system': jupypaths.SYSTEM_CONFIG_PATH[0]}

    return {k: os.path.join(v, 'nbconfig') for k,v in cdirs.items()}


def location_writable():
    config_paths = jupyter_config_dirs()
    ext_paths = nbextension_ordered_paths()
    writable = {}
    for location in ext_paths:
        writable[location] = (
            os.access(config_paths[location], os.W_OK | os.X_OK) and
            os.access(ext_paths[location], os.W_OK | os.X_OK))
    return writable


def preferred_install_location():
    versions = get_installed_versions('nbmolviz', True)
    for loc in 'environment user system'.split():
        if versions[loc].writable:
            preferred_loc = loc
            return preferred_loc
    else:
        return None


def autoinstall():
    """ Attempt to install and activate the notebook extensions

    Raises:
        ValueError: if there are no writable install locations
    """
    from moldesign import compute
    from . import __version__ as nbv_version
    from . import widget_utils as wu

    preferred = preferred_install_location()
    if preferred is None:
        raise ValueError("Cannot install extensions - none of the directories are writable!")

    state = wu.extensions_install_check()
    for dep in state:
        do_install = False
        if not state[dep]['installed'] or state[dep]['enabled'] != state[dep]['installed']:
            print("Activating '%s' extensions:" % dep)
            do_install = True
        elif (dep == 'nbmolviz' and
                  not compute.config.get('skip_nbmolviz_version_check', False) and
                  state[dep]['installed'] and
                  state[dep]['version'] != nbv_version):
            print("Updating 'nbmolviz' extensions from %s to %s:" % (state[dep]['version'],
                                                                     nbv_version))
            do_install = True
        else:
            print("'%s' extensions already activated." % dep)

        if do_install:
            activate_extension(dep, FLAGS[preferred])



def get_installed_versions(pyname, getversion):
    """ Check if the required NBExtensions are installed. If not, prompt user for action.
    """
    import importlib
    from notebook import nbextensions

    spec = importlib.import_module(pyname)._jupyter_nbextension_paths()[0]
    extname = spec['dest']
    require = spec['require']
    assert spec['section'] == 'notebook'

    search_paths = nbextension_ordered_paths()
    writable = location_writable()

    installed = {k: nbextensions.check_nbextension(extname, **EXTENSION_KWARGS[k])
                 for k in search_paths.keys()}

    config_dirs = jupyter_config_dirs()
    paths = {}
    versions = {}
    enabled = {}
    active = {}
    found_active = False
    for location in EXTENSION_KWARGS:
        if not installed[location]:
            active[location] = False
            continue

        active[location] = not found_active
        found_active = True
        paths[location] = os.path.join(search_paths[location], 'nbextensions', extname)
        config = nbextensions.BaseJSONConfigManager(config_dir=config_dirs[location])
        enabled[location] = require in config.get('notebook').get('load_extensions', {})

        if getversion:
            versionfile = os.path.join(paths[location], 'VERSION')
            if installed[location] and os.path.exists(versionfile):
                with open(versionfile, 'r') as pfile:
                    versions[location] = pfile.read().strip()
            else:
                versions[location] = 'pre-0.7'

    return {k: NbExtVersion(extname,
                            installed[k],
                            paths.get(k, None),
                            versions.get(k, None),
                            enabled.get(k, False),
                            active[k],
                            writable[k])
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
