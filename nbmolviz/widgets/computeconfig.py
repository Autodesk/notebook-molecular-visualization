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

import io
import os
import base64
import collections

from pip._vendor.packaging import version
import ipywidgets as ipy

import moldesign as mdt
from moldesign import compute

from ..uielements import StyledTab
from ..uielements.components import HBox, VBox
from ..widget_utils import process_widget_kwargs


def configure():
    from IPython.display import display
    display(MDTConfig())

# Some synonyms
about = configure

MISSING = u'\u274C'
INSTALLED = u"\u2705"


class MDTConfig(VBox):
    def __init__(self):
        self.interface_status = InterfaceStatus()
        self.compute_config = DockerConfig()
        self.changelog = ChangeLog()
        self.tab_list = StyledTab([ipy.Box(), self.interface_status, self.compute_config, self.changelog])
        self.tab_list.set_title(0, '^')
        self.tab_list.set_title(1, "Interfaces")
        self.tab_list.set_title(2, 'Docker configuration')
        self.tab_list.set_title(3, "What's new")
        self.children = [self.make_header(), self.tab_list]
        super().__init__(children=self.children)

    def make_header(self):
        img = io.open(os.path.join(mdt.PACKAGEPATH, '_static_data/img/banner.png'), 'r+b').read()
        encoded = base64.b64encode(img).decode('ascii')
        img = '<img style="max-width:100%" src=data:image/png;base64,'+('%s>'%encoded)
        links = [self._makelink(*args) for args in
                   (("http://moldesign.bionano.autodesk.com/", 'About'),
                    ("https://github.com/autodesk/molecular-design-toolkit/issues", 'Issues'),
                    ("http://bionano.autodesk.com/MolecularDesignToolkit/explore.html",
                     "Tutorials"),
                    ('http://autodesk.github.io/molecular-design-toolkit/', 'Documentation'),
                    ('https://lifesciences.autodesk.com/', 'Adsk LifeSci')
                    )]
        linkbar = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'.join(links)
        return ipy.HTML(("<span style='float:left;font-size:0.8em;font-weight:bold'>Version: "
                         "{version}</span>"
                         "<span style='float:right'>{linkbar}</span>"
                         "<p>{img}</p>").format(img=img, linkbar=linkbar, version=mdt.__version__))

    @staticmethod
    def _makelink(url, text):
        return '<a href="{url}" target="_blank" title="{text}">{text}</a>'.format(url=url,
                                                                                  text=text)


class InterfaceStatus(VBox):
    def __init__(self):
        from moldesign.compute import packages

        self.css = ipy.HTML('<style> '
                            '.nbmolviz-table-header{border-bottom-style:solid;'
                            '                       display:inline-block;'
                            '                       border-bottom-width:1px} '
                            '.nbmolviz-table-row{border-bottom-style:dotted;'
                            '                    display:inline-block;'
                            '                    border-bottom-width:1px;'
                            '                    padding-bottom:3px} '
                            '.nbmolviz-monospace{font-family:monospace} '
                            '.nbv-width-lg{width:310px} '
                            '.nbv-width-med{width:125px; display:inline-block} '
                            '.nbv-width-sm{width:60px;display:inline-block} '
                            '.nbv-leftborder{border-left-style:solid;'
                            '                border-left-width:2px;}'
                            '</style>')

        self.toggle = ipy.ToggleButtons(options=['Python libs', 'Executables'],
                                        value='Python libs')
        self.toggle.observe(self.switch_pane, 'value')

        self.pyheader = ipy.HTML(
                '<span class="nbmolviz-table-header nbv-width-med">Package</span> '
                '<span class="nbmolviz-table-header nbv-width-sm">Local version</span> '
                '<span class="nbmolviz-table-header nbv-width-sm">Expected version</span>'
                '<span class="nbv-width-sm">&nbsp;</span>'  # empty space
                '<span class="nbmolviz-table-header nbv-width-lg">'
                '          Run calculations...</span>'
                '<span class="nbmolviz-table-header nbv-width-med"> &nbsp;</span>')
        self.python_libs = ipy.VBox([self.pyheader] + [PyLibConfig(p) for p in packages.packages])

        self.exeheader = ipy.HTML(
                '<span class="nbmolviz-table-header nbv-width-med">Program</span> '
                '<span class="nbmolviz-table-header nbv-width-sm">Local version</span> '
                '<span class="nbmolviz-table-header nbv-width-sm">Docker version</span>'
                '<span class="nbv-width-sm">&nbsp;</span>'  # empty space
                '<span class="nbmolviz-table-header nbv-width-lg">'
                '          Run calculations...</span>'
                '<span class="nbmolviz-table-header nbv-width-med"> &nbsp;</span>')
        self.executables = ipy.VBox([self.exeheader] + [ExeConfig(p) for p in packages.executables])

        self.children = [self.toggle, self.css, self.python_libs]
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
                ('<span class="nbmolviz-table-row nbv-width-med nbmolviz-monospace">'
                 '           {xface.packagename}</span> '
                 '<span class="nbmolviz-table-row nbmolviz-monospace nbv-width-sm">'
                 '                {localversion}</span> '
                 '<span class="nbmolviz-table-row nbmolviz-monospace nbv-width-sm">'
                 '                {xface.expectedversion}</span>'
                 '<span class="nbv-width-sm nbmolviz-table-row">&nbsp;</span>'  # empty space
                 )
                    .format(xface=xface,
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
        self.selector.add_class("nbmolviz-table-row")

        children = [self.maintext, self.selector]

        if not self.xface.required and self.xface.is_installed():
            self.save_button = ipy.Button(description='Make default')
            self.save_button.on_click(self.save_selection)
            self.save_button.add_class('nbmolviz-table-row')
            children.append(self.save_button)

        super().__init__(children=children,
                         layout=ipy.Layout(width='100%', align_items='flex-end'))

    def _toggle(self, *args):
        self.xface.force_remote = (self.selector.value == 'in docker')

    def save_selection(self, *args):
        compute.update_saved_config(
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
                ('<span class="nbmolviz-table-row nbv-width-med nbmolviz-monospace">'
                 '           {xface.name}</span> '
                 '<span class="nbmolviz-table-row nbmolviz-monospace nbv-width-sm">'
                 '                {localversion}</span> '
                 '<span class="nbmolviz-table-row nbmolviz-monospace nbv-width-sm">'
                 '                {xface.expectedversion}</span>'
                 '<span class="nbv-width-sm nbmolviz-table-row">&nbsp;</span>'  # empty space
                 )
                    .format(xface=xface, localversion=v))

        self.selector = ipy.ToggleButtons(options=['in docker', 'locally'],
                                          value='in docker',
                                          button_style='info')
        self.selector.add_class('nbv-width-lg')
        self.selector.add_class("nbmolviz-table-row")

        self.selector.observe(self._toggle, 'value')
        self.path = ipy.HTML(layout=ipy.Layout(width='150px', font_size='x-small'),
                              value=xface.path if xface.path is not None else '',)

        self.save_button = ipy.Button(description='Make default', layout=ipy.Layout(width='100px'))
        self.save_button.on_click(self.save_selection)
        self.save_button.add_class('nbmolviz-table-row')

        children = [self.maintext, self.selector, self.save_button]

        super().__init__(children=children,
                         layout=ipy.Layout(width='100%', align_items='flex-end'))

    def _toggle(self, *args):
        self.xface.run_local = (self.selector.value == 'locally')

    def save_selection(self, *args):
        compute.update_saved_config(
                run_local={self.xface.name: self.selector.value == 'locally'})


class ChangeLog(ipy.Box):
    def __init__(self):
        super().__init__()
        try:
            current = version.parse(mdt.__version__)
            latest = self.version_check()
            if current >= latest:
                versiontext = 'Up to date. Latest release: %s' % latest
            else:
                versiontext = ('New release available! '
                               '(Current: %s, latest: %s <br>' % (current, latest) +
                               '<b>Install it:</b> '
                               '<span style="font-family:monospace">pip install -U moldesign'
                               '</span>')
        except Exception as e:
            versiontext = '<b>Failed update check</b>: %s' % e

        self.version = ipy.HTML(versiontext)
        self.textarea = ipy.Textarea(layout=ipy.Layout(width='700px', height='300px'))

        p1 = os.path.join(mdt.PACKAGEPATH, "HISTORY.rst")
        p2 = os.path.join(mdt.PACKAGEPATH, "..", "HISTORY.rst")
        if os.path.exists(p1):
            path = p1
        elif os.path.exists(p2):
            path = p2
        else:
            path = None

        if path is not None:
            with open(path, 'r') as infile:
                self.textarea.value = infile.read()
        else:
            self.textarea.value = 'HISTORY.rst not found'

        self.textarea.disabled = True
        self.children = (self.version, self.textarea)

    @staticmethod
    def version_check():
        """
        References:
            http://code.activestate.com/recipes/577708-check-for-package-updates-on-pypi-works-best-in-pi/
        """
        import xmlrpc.client
        pypi = xmlrpc.client.ServerProxy('https://pypi.python.org/pypi')
        return version.parse(pypi.package_releases('moldesign')[0])


class DockerConfig(VBox):
    def __init__(self):
        super().__init__()

        self.engine_config_description = ipy.HTML('Docker host with protocol and port'
                                                  ' (e.g., "http://localhost:2375"). If blank, this'
                                                  ' defaults to the docker engine configured at '
                                                  'your command line.',
                                                  layout=ipy.Layout(width='100%'))
        self.engine_config_value = ipy.Text('blank', layout=ipy.Layout(width='100%'))

        self._reset_config_button = ipy.Button(description='Reset',
                                               tooltip='Reset to applied value')
        self._apply_changes_button = ipy.Button(description='Apply',
                                                tooltip='Apply for this session')
        self._save_changes_button = ipy.Button(description='Make default',
                                               tooltip='Make this the default for new sessions')
        self._test_button = ipy.Button(description='Test connection',
                                       tooltip='Test connection to docker engine')
        self._reset_config_button.on_click(self.reset_config)
        self._apply_changes_button.on_click(self.apply_config)
        self._save_changes_button.on_click(self.save_config)
        self._test_button.on_click(self.test_connection)

        self.children = [VBox([self.engine_config_description,
                               self.engine_config_value]),
                         HBox([self._reset_config_button,
                               self._apply_changes_button,
                               self._test_button,
                               self._save_changes_button]),
                         ]
        self.reset_config()

    def reset_config(self, *args):
        """ Reset configuration in UI widget to the stored values
        """
        self.engine_config_value.value = compute.config['default_docker_host']

    def apply_config(self, *args):
        compute.config['default_docker_host'] = self.engine_config_value.value
        compute.reset_compute_engine()

    def test_connection(self, *args):
        self.apply_config()
        engine = compute.default_engine
        if engine is None:
            raise ValueError('Failed to create compute engine with current configuration')
        engine.test_connection()
        print("SUCCESS: %s is accepting jobs" % engine)

    def save_config(self, *args):
        compute.update_saved_config(dockerhost=self.engine_config_value.value)


class RegistryConfig(ipy.Box):
    def __init__(self):
        super().__init__(
                **process_widget_kwargs(dict(flex_flow='column')))
        self.repo_field = ipy.Text(description='Image repository')
        self.version_field = ipy.Text(description='Image version')

        self._reset_config_button = ipy.Button(description='Reset',
                                               tooltip='Reset to current configuration')

        self._apply_changes_button = ipy.Button(description='Apply',
                                                tooltip='Apply for this session')
        self._save_changes_button = ipy.Button(description='Make default',
                                               tooltip='Make this the default for new sessions')
        self._pull_button = ipy.Button(description='Pull images',
                                       tooltip=
                                       'Download all moldesign images to the compute engine')

        self.children = (HBox([self.repo_field, self.version_field]),
                         HBox([self._reset_config_button,
                                                self._apply_changes_button,
                                                self._pull_button]))

        self._reset_config_button.on_click(self.reset_config)
        self._apply_changes_button.on_click(self.apply_config)
        self._save_changes_button.on_click(self.save_config)
        self._test_button.on_click(self.test_connection)

    def reset_config(self, *args):
        self.repo_field.value = mdt.compute.config.default_repository
        self.version_field.value = mdt.compute.config.version_tag

    def apply_config(self, *args):
        compute.config.default_repository = self.repo_field.value
        compute.config.version_tag = self.version_field.value


_enginedefs = (
    ('free-compute-cannon', {'displayname': "Public CloudComputeCannon Demo",
                             'hostdescription': 'Autodesk-sponsored cloud compute server',
                             'configkey': 'default_ccc_host',
                             'aliases': ('ccc', 'cloudcomputecannon')
                             }),

    ('cloud-compute-cannon', {'displayname': 'CloudComputeCannon',
                              'hostdescription': 'Server address and port (e.g.,   '
                                                 '"192.168.0.1:9000")',
                              'configkey': 'default_ccc_host',
                              'aliases': ('ccc', 'cloudcomputecannon')}),

    ('docker', {'displayname': 'Docker',
                'hostdescription': 'Docker host with port (e.g., "localhost:2375")',
                'configkey': 'default_docker_host',
                'aliases': ('docker',)
                }),

    ('docker-machine', {'displayname': 'Docker Machine',
                        'hostdescription': 'Name of docker-machine (e.g., "default")',
                        'configkey': 'default_docker_machine',
                        'aliases': ('docker-machine',)
                        }),
)

ENGINES = collections.OrderedDict(_enginedefs)
ENGINE_DISPLAY = collections.OrderedDict((v['displayname'],k) for k,v in ENGINES.items())