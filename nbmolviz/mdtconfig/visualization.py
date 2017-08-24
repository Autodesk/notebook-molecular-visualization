# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
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

import ipywidgets
import traitlets

from ..uielements.components import VBox, HBox
from .. import install

MISSING = u'\u274C'
INSTALLED = u"\u2705"


class MdtExtensionConfig(VBox):
    def __init__(self):
        self.reload_msg = ipywidgets.HTML(
                "<b>Note:</b> To see the effects of any changes, you should first "
                "save your notebook, then reload this page.")
        self.nbv_config = NBExtensionConfig('nbmolviz', True)
        self.widgets_config = NBExtensionConfig('widgetsnbextension')
        super().__init__(children=[self.reload_msg, self.nbv_config, self.widgets_config])


class NBExtensionConfig(VBox):
    LABELS = {'environment': 'this virtualenv',
              'system': 'all users',
              'user': 'this user'}

    HEADER = ('<span class="nbv-width-med nbv-table-header">Installed for:</span>'
              '<span class="nbv-width-sm nbv-table-header">Installed</span>'
              '<span class="nbv-width-sm nbv-table-header">Enabled</span>'
              '<span class="nbv-width-sm nbv-table-header">Writable</span>'
              '<span class="nbv-width-lg nbv-table-header">Path</span>'
              '<span class="nbv-width-lg nbv-table-header">&nbsp;</span>')

    state = traitlets.Dict()

    def __init__(self, pyname, getversion=False):
        self.displays = {}
        self.pyname = pyname
        self.getversion = getversion

        self.nbv_display = VBox()
        self.widgets_display = VBox()
        self.warning = ipywidgets.HTML()

        super().__init__()
        children = [ipywidgets.HTML("<h4><center>%s</center></h4>" % self.pyname,
                                    layout=ipywidgets.Layout(align_self='center')),
                    ipywidgets.HTML(self.HEADER)]

        for location in install.nbextension_ordered_paths():
            self.state = install.get_installed_versions(self.pyname, self.getversion)
            props = self._get_props(location)
            self.displays[location] = ExtensionInstallLocation(self, props)
            children.append(self.displays[location])

        children.append(self.warning)

        self.children = children
        self._highlight_active()

    def _update_state(self):
        self.state = install.get_installed_versions(self.pyname, self.getversion)

    def _highlight_active(self):
        num_installed = 0
        for location in install.nbextension_ordered_paths():
            if self.state[location].active:
                self.displays[location].layout.border = 'solid #9feeb2'
            else:
                assert not self.state[location].active
                self.displays[location].layout.border = '#000000'
                self.displays[location].layout.send_state('border')
            if self.state[location].installed: num_installed += 1

        if num_installed == 0:
            self.warning.value = (
                u'⚠ %s extensions must be installed for notebook visualization.'
                % self.pyname)
        elif num_installed == 1:
            self.warning.value = ''
        elif num_installed > 1:
            self.warning.value = ('%s is installed in more than one location. Jupyter will use the '
                                  'location highlighted above.') % self.pyname

    def _get_props(self, location):
        props = {f: getattr(self.state[location], f) for f in self.state[location]._fields}
        props['location'] = location
        props['writable'] = INSTALLED if props['writable'] else MISSING
        if not props['installed']:
            assert props['path'] is props['version'] is None
            props['version'] = MISSING
            props['enabled'] = MISSING
            props['path'] = '--'

        else:
            props['path'] = props['path'].replace("/", "/<wbr />")
            if not props['version']:
                props['version'] = INSTALLED
            else:
                props['version'] = '%s<p>%s</p>' % (props['version'], INSTALLED)

            props['enabled'] = INSTALLED if props['enabled'] else MISSING

        props.update({'label': self.LABELS.get(location, location),
                      'pyname': self.pyname,
                      'flags': install.FLAGS[location]
                      })
        return props


class ExtensionInstallLocation(HBox):
    RENDER = ('<span class="nbv-width-med nbv-table-row"><b>{label}</b></span>'
              '<span class="nbv-width-sm nbv-monospace nbv-oflow-ellipsis nbv-table-row">'
              '{version}</span>'
              '<span class="nbv-width-sm nbv-table-row"><b>{enabled}</b></span>'
              '<span class="nbv-width-sm nbv-table-row"><b>{writable}</b></span>'
              '<span class="nbv-width-lg nbv-monospace nbv-table-row">{path}</span>')

    def __init__(self, parent, props):
        super().__init__(layout=ipywidgets.Layout(align_items='flex-end'))
        self.parent = parent
        self.props = props
        self.install_button = ipywidgets.Button()
        self.install_button.add_class('nbv-table-row')
        self.remove_button = ipywidgets.Button(description='remove')
        self.remove_button.add_class('nbv-table-row')
        self.html = ipywidgets.HTML()

        if self.props['writable'] == 'INSTALLED':
            self.chidlren = (self.html,)
        else:
            self.children = (self.html, self.install_button, self.remove_button)
        self.install_button.on_click(self.install)
        self.remove_button.on_click(self.uninstall)
        self.rerender()

    def rerender(self):
        self.props = self.parent._get_props(self.props['location'])
        if self.props['enabled'] and self.props['installed']:
            self.install_button.description = 'reinstall'
        elif self.props['enabled']:
            self.install_button.description = 'install'
        elif self.props['installed']:
            self.install_button.description = 'enable'
        else:
            self.install_button.description = 'install'
        self.html.value = self.RENDER.format(**self.props)

    def install(self, *args):
        install.activate_extension(self.props['pyname'], self.props['flags'])
        self.parent._update_state()
        self.parent._highlight_active()
        self.rerender()

    def uninstall(self, *args):
        install.deactivate_extension(self.props['pyname'], self.props['flags'])
        self.parent._update_state()
        self.parent._highlight_active()
        self.rerender()










