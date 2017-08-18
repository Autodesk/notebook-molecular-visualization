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

class DockerConfig(VBox):
    def __init__(self):
        self.devmode_button = ipy.Checkbox(description='Build my own images (developer mode)',
                                           value=mdt.compute.config.devmode,
                                           layout=ipy.Layout(width='500px'))
        self.devmode_button.observe(self.set_devmode, 'value')

        self.engine_config_description = ipy.HTML('Docker host with protocol and port'
                                                  ' (e.g., "http://localhost:2375"). If blank, this'
                                                  ' defaults to the docker engine configured at '
                                                  'your command line.',
                                                  layout=ipy.Layout(width='100%'))
        self.engine_config_value = ipy.Text('blank', layout=ipy.Layout(width='100%'))

        self.image_box = ipy.Box()

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

        self.children = [self.devmode_button,
                         VBox([self.engine_config_description,
                               self.engine_config_value]),
                         HBox([self._reset_config_button,
                               self._apply_changes_button,
                               self._test_button,
                               self._save_changes_button]),
                         self.image_box
                         ]
        self.reset_config()
        super().__init__(children=self.children)

    def reset_config(self, *args):
        """ Reset configuration in UI widget to the stored values
        """
        self.engine_config_value.value = mdt.compute.config['default_docker_host']
        self.set_devmode()

    def set_devmode(self, *args):
        mdt.compute.config.devmode = self.devmode_button.value
        self.image_box.children = (DockerImageStatus(),)

    def apply_config(self, *args):
        mdt.compute.config['default_docker_host'] = self.engine_config_value.value
        mdt.compute.reset_compute_engine()

    def test_connection(self, *args):
        self.apply_config()
        engine = mdt.compute.default_engine
        if engine is None:
            raise ValueError('Failed to create compute engine with current configuration')
        engine.test_connection()
        print("SUCCESS: %s is accepting jobs" % engine)

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