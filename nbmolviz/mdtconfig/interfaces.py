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
import ipywidgets as ipy
import moldesign as mdt
from ..uielements.components import VBox

MISSING = u'\u274C'
INSTALLED = u"\u2705"


class InterfaceStatus(VBox):
    def __init__(self):
        from moldesign.compute import packages

        self.toggle = ipy.ToggleButtons(options=['Python libs', 'Executables'],
                                        value='Python libs')
        self.toggle.observe(self.switch_pane, 'value')

        self.pyheader = ipy.HTML(
                '<span class="nbv-table-header nbv-width-med">Package</span> '
                '<span class="nbv-table-header nbv-width-sm">Local version</span> '
                '<span class="nbv-table-header nbv-width-sm">Expected version</span>'
                '<span class="nbv-width-sm">&nbsp;</span>'  # empty space
                '<span class="nbv-table-header nbv-width-lg">'
                '          Run calculations...</span>'
                '<span class="nbv-table-header nbv-width-med"> &nbsp;</span>')
        self.python_libs = ipy.VBox([self.pyheader] + [PyLibConfig(p) for p in packages.packages])

        self.exeheader = ipy.HTML(
                '<span class="nbv-table-header nbv-width-med">Program</span> '
                '<span class="nbv-table-header nbv-width-sm">Local version</span> '
                '<span class="nbv-table-header nbv-width-sm">Docker version</span>'
                '<span class="nbv-width-sm">&nbsp;</span>'  # empty space
                '<span class="nbv-table-header nbv-width-lg">'
                '          Run calculations...</span>'
                '<span class="nbv-table-header nbv-width-med"> &nbsp;</span>')
        self.executables = ipy.VBox([self.exeheader] + [ExeConfig(p) for p in packages.executables])

        self.children = [self.toggle, self.python_libs]
        super().__init__(children=self.children)

    def switch_pane(self, *args):
        children = list(self.children)

        if self.toggle.value == 'Python libs':
            children[-1] = self.python_libs
        else:
            assert self.toggle.value == 'Executables'
            children[-1] = self.executables

        self.children = children


class PyLibConfig(ipy.HBox):
    def __init__(self, xface):
        self.xface = xface
        if self.xface.is_installed():
            version_string = xface.installed_version()
            if not version_string:
                version_string = 'unknown'

            if version_string != xface.expectedversion:
                version_string = '<span style="color:red">%s</span>' % version_string

        self.maintext = ipy.HTML(
                ('<span class="nbv-table-row nbv-width-med nbv-monospace">'
                 '           {xface.packagename}</span> '
                 '<span class="nbv-table-row nbv-monospace nbv-width-sm">'
                 '                {localversion}</span> '
                 '<span class="nbv-table-row nbv-monospace nbv-width-sm">'
                 '                {xface.expectedversion}</span>'
                 '<span class="nbv-width-sm nbv-table-row">&nbsp;</span>'  # empty space
                 ).format(xface=xface,
                            localversion=(version_string if self.xface.is_installed()
                                                          else MISSING)))

        if xface.required:
            self.selector = ipy.ToggleButtons(options=['locally'])
        elif not xface.is_installed():
            self.selector = ipy.ToggleButtons(options=['in docker'],
                                              button_style='warning')
        else:
            self.selector = ipy.ToggleButtons(options=['locally', 'in docker'],
                                              value='in docker' if xface.force_remote else 'locally',
                                              button_style='info')
            self.selector.observe(self._toggle, 'value')

        self.selector.add_class('nbv-width-lg')
        self.selector.add_class("nbv-table-row")

        children = [self.maintext, self.selector]

        if not self.xface.required and self.xface.is_installed():
            self.save_button = ipy.Button(description='Make default')
            self.save_button.on_click(self.save_selection)
            self.save_button.add_class('nbv-table-row')
            children.append(self.save_button)

        super().__init__(children=children,
                         layout=ipy.Layout(width='100%', align_items='flex-end'))

    def _toggle(self, *args):
        self.xface.force_remote = (self.selector.value == 'in docker')

    def save_selection(self, *args):
        mdt.compute.update_saved_config(
                run_remote={self.xface.name: self.selector.value == 'in docker'})


class ExeConfig(ipy.HBox):
    def __init__(self, xface):
        self.xface = xface

        if xface.is_installed():
            if xface.version_flag:
                v = xface.get_installed_version()
            else:
                v = INSTALLED
        else:
            v = MISSING

        self.maintext = ipy.HTML(
                ('<span class="nbv-table-row nbv-width-med nbv-monospace">'
                 '           {xface.name}</span> '
                 '<span class="nbv-table-row nbv-monospace nbv-width-sm">'
                 '                {localversion}</span> '
                 '<span class="nbv-table-row nbv-monospace nbv-width-sm">'
                 '                {xface.expectedversion}</span>'
                 '<span class="nbv-width-sm nbv-table-row">&nbsp;</span>'  # empty space
                 )
                    .format(xface=xface, localversion=v))

        self.selector = ipy.ToggleButtons(options=['in docker', 'locally'],
                                          value='in docker',
                                          button_style='info')
        self.selector.add_class('nbv-width-lg')
        self.selector.add_class("nbv-table-row")

        self.selector.observe(self._toggle, 'value')
        self.path = ipy.HTML(layout=ipy.Layout(width='150px', font_size='x-small'),
                              value=xface.path if xface.path is not None else '',)

        self.save_button = ipy.Button(description='Make default', layout=ipy.Layout(width='100px'))
        self.save_button.on_click(self.save_selection)
        self.save_button.add_class('nbv-table-row')

        children = [self.maintext, self.selector, self.save_button]

        super().__init__(children=children,
                         layout=ipy.Layout(width='100%', align_items='flex-end'))

    def _toggle(self, *args):
        self.xface.run_local = (self.selector.value == 'locally')

    def save_selection(self, *args):
        mdt.compute.update_saved_config(
                run_local={self.xface.name: self.selector.value == 'locally'})
