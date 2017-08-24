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
import collections
import ipywidgets as ipy
import moldesign as mdt
from ..uielements.components import VBox, HBox
from ..widget_utils import process_widget_kwargs
from .images import DockerImageStatus


SPINNER = '<div class="nbv-loader" />'
CONNECTED = '<span style="color:green">connected</span>'
DISCONNECTED = '<span style="color:red">disconnected</span>'

class DockerConfig(VBox):
    def __init__(self):
        self.client = None
        self.warning = ipy.HTML(description='<b>Engine status:</b>', value=SPINNER)
        self.devmode_label = ipy.Label('Use local docker images (developer mode)',
                                       layout=ipy.Layout(width='100%'))
        self.devmode_button = ipy.Checkbox(value=mdt.compute.config.devmode,
                                           layout=ipy.Layout(width='15px'))
        self.devmode_button.observe(self.set_devmode, 'value')

        self.engine_config_description = ipy.HTML('Docker host with protocol and port'
                                                  ' (e.g., <code>http://localhost:2375</code>).'
                                                  ' If blank, this'
                                                  ' defaults to the docker engine configured at '
                                                  'your command line.',
                                                  layout=ipy.Layout(width='100%'))
        self.engine_config_value = ipy.Text('blank', layout=ipy.Layout(width='100%'))
        self.engine_config_value.add_class('nbv-monospace')

        self.image_box = ipy.Box()

        self._reset_config_button = ipy.Button(description='Reset',
                                               tooltip='Reset to applied value')
        self._apply_changes_button = ipy.Button(description='Apply',
                                                tooltip='Apply for this session')
        self._save_changes_button = ipy.Button(description='Make default',
                                               tooltip='Make this the default for new sessions')
        self._reset_config_button.on_click(self.reset_config)
        self._apply_changes_button.on_click(self.apply_config)
        self._save_changes_button.on_click(self.save_config)

        self.children = [self.warning,
                         VBox([self.engine_config_description,
                               self.engine_config_value]),
                         HBox([self._reset_config_button,
                               self._apply_changes_button,
                               self._save_changes_button]),
                         HBox([self.devmode_button, self.devmode_label]),
                         self.image_box]
        self.reset_config()
        super().__init__(children=self.children)
        self.connect_to_engine()

    def reset_config(self, *args):
        """ Reset configuration in UI widget to the stored values
        """
        self.engine_config_value.value = mdt.compute.config['default_docker_host']

    def set_devmode(self, *args):
        self.image_box.children = ()
        mdt.compute.config.devmode = self.devmode_button.value
        self.image_box.children = (DockerImageStatus(self.client),)

    def apply_config(self, *args):
        mdt.compute.config['default_docker_host'] = self.engine_config_value.value
        self.connect_to_engine()

    def connect_to_engine(self, *args):
        self.warning.value = SPINNER
        self.client = None
        try:
            mdt.compute.reset_compute_engine()
            self.client = mdt.compute.get_engine().client
            self.client.ping()
        except (mdt.exceptions.DockerError, AttributeError):
            self.warning.value = DISCONNECTED
        else:
            self.image_box.children = (DockerImageStatus(self.client),)
            self.warning.value = CONNECTED

    def save_config(self, *args):
        mdt.compute.update_saved_config(dockerhost=self.engine_config_value.value)


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
        mdt.compute.config.default_repository = self.repo_field.value
        mdt.compute.config.version_tag = self.version_field.value


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