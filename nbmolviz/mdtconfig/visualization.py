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
        self.nbv_config = NBExtensionConfig('nbmolviz-js', 'nbmolviz', True)
        self.widgets_config = NBExtensionConfig('jupyter-js-widgets', 'widgetsnbextension')
        super().__init__(children=[self.nbv_config, self.widgets_config])


class NBExtensionConfig(VBox):
    FLAGS = {'environment': '--sys-prefix',
             'system': '--sys',
             'user': '--user'}

    LABELS = {'environment': 'this virtualenv',
              'system': 'all users',
              'user': 'this user'}

    HEADER = ('<span class="nbv-width-med nbv-table-header">Installed for:</span>'
              '<span class="nbv-width-med nbv-table-header">Version</span>'
              '<span class="nbv-width-lg nbv-table-header">Path</span>'
              '<span class="nbv-width-lg nbv-table-header">&nbsp;</span>')

    state = traitlets.Dict()

    def __init__(self, extname, pyname, getversion=False):
        from .. import install
        self.extname = extname
        self.pyname = pyname

        self.nbv_display = VBox()
        self.widgets_display = VBox()

        super().__init__()

        self.state = install.get_installed_versions(extname, getversion)

        children = [ipywidgets.HTML("<h4>%s</h4>" % self.extname),
                    ipywidgets.HTML(self.HEADER)]

        for key, value in self.state.items():
            props = {f:getattr(value, f) for f in value._fields}
            if not props['installed']:
                assert props['path'] is props['version'] is None
                props['version'] = MISSING
                props['path'] = 'not installed'

            else:
                props['path'] = props['path'].replace("/", "/<wbr />")
                if not props['version']:
                    props['version'] = '??'

            props.update({'label':self.LABELS.get(key, key),
                          'pyname': pyname,
                          'flags': self.FLAGS[key]
                          })
            children.append(ExtensionInstallLocation(props))

        self.children = children


class ExtensionInstallLocation(HBox):
    RENDER = ('<span class="nbv-width-med nbv-table-row"><b>{label}</b></span>'
              '<span class="nbv-width-med nbv-monospace nbv-oflow-ellipsis nbv-table-row">{version}</span>'
              '<span class="nbv-width-lg nbv-monospace nbv-table-row">{path}</span>')

    def __init__(self, props):
        super().__init__(layout=ipywidgets.Layout(align_items='flex-end'))
        self.props = props
        self.install_button = ipywidgets.Button(description='reinstall')
        self.install_button.add_class('nbv-table-row')
        self.remove_button = ipywidgets.Button(description='remove')
        self.remove_button.add_class('nbv-table-row')

        self.children = (ipywidgets.HTML(self.RENDER.format(**self.props)),
                         self.install_button, self.remove_button)
        self.install_button.on_click(self.install)
        self.remove_button.on_click(self.install)

    def install(self, *args):
        install.activate_extension(self.props['pyname'], self.props.flags)

    def uninstall(self, *args):
        install.deactivate_extension(self.props['pyname'], self.props.flags)









