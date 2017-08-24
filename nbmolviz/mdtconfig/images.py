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
import threading
import subprocess
import sys
import os
import ipywidgets as ipy
import moldesign as mdt

MISSING = u'\u274C'
INSTALLED = u"\u2705"
WARNING = u"⚠️"


class DockerImageStatus(ipy.VBox):
    def __init__(self, client):
        self.client = client

        images = self._get_images()
        self.header = ipy.HTML(
                '<span class="nbv-table-header" style="width:950px"">Image status</span>',
                layout=ipy.Layout(align_items='flex-end'))
        super().__init__([self.header] + [DockerImageView(im, client) for im in sorted(images)])

    def _get_images(self):
        return set(p.get_docker_image_path()
                   for p in mdt.compute.packages.executables + mdt.compute.packages.packages)


class DockerImageView(ipy.HBox):
    LOADER = "<div class='nbv-loader' />"
    DMKDIR = os.path.join(os.path.dirname(os.path.dirname(mdt.__file__)), 'DockerMakefiles')

    def __init__(self, image, client):
        self._err = False
        self._client = client
        self.image = image
        self.status = ipy.HTML(layout=ipy.Layout(width="20px"))
        self.html = ipy.HTML(value=image, layout=ipy.Layout(width="400px"))
        self.html.add_class('nbv-monospace')
        self.msg = ipy.HTML(layout=ipy.Layout(width='300px'))
        self.button = ipy.Button(layout=ipy.Layout(width='100px'))
        if mdt.compute.config.devmode:
            self.button.on_click(self.rebuild)
        else:
            self.button.on_click(self.pull)
        self._reactivate_button()
        self._set_status_value()
        super().__init__(children=[self.status, self.html, self.button, self.msg])

    def rebuild(self, *args):
        if not os.path.isdir(self.DMKDIR):
            raise ValueError('Could not locate the docker makefiles. '
                             'To run MDT in development mode, '
                             'clone the molecular-design-toolkit repository and install it using '
                             '`pip install -e`.')

        namefields = self.image.split(':')
        assert len(namefields) == 2 and namefields[1] == 'dev'
        self._disable_button('Rebuilding...')

        thread = threading.Thread(target=self._run_rebuild, args=[namefields[0]])
        thread.start()

    def _run_rebuild(self, targetname):
        try:
            self.msg.value = 'Running <code>docker-make</code>'
            cmd = ['docker-make', '--tag', 'dev',targetname]
            self.status.value = self.LOADER
            print('> %s' % ' '.join(cmd))
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       cwd=self.DMKDIR)
            for line in process.stdout:
                sys.stdout.write(line)
        except Exception as e:
            self._err = True
            self.msg.value = str(e)
            raise

        finally:
            self._reactivate_button()
            self._set_status_value()
            if not self._err:
                self.msg.value = 'Rebuilt <code>%s</code> successfully.' % self.image

    def pull(self, *args):
        self.button.disabled = True
        self._err = False
        thread = threading.Thread(target=self._run_pull)
        thread.start()

    def _run_pull(self):
        from docker import errors
        try:
            self._disable_button('Pulling...')
            self.status.value = self.LOADER
            self.msg.value = 'Starting download.'

            try:
                response = self._client.pull(self.image, stream=True, decode=True)
                self._watch_pull_logs(response)
            except errors.NotFound as exc:
                self._err = True
                self.msg.value = 'ERROR: %s' % exc.explanation

        except Exception as e:
            self._err = True
            self.msg = str(e)
            raise

        finally:
            self._set_status_value()
            self._reactivate_button()
            if not self._err:
                self.msg.value = 'Pull successful.'

    def _disable_button(self, description):
        self.button.disabled = True
        self.button.description = description
        self.button.style.font_weight = '100'
        self.button.style.button_color = 'lightgray'

    def _reactivate_button(self):
        self.button.disabled = False
        if self._client is None:
            self.button.description = 'no connection'
            self.button.disabled = True
            self.button.style.button_color = '#FAFAFA'
        else:
            if mdt.compute.config.devmode:
                self.button.description = 'Rebuild image'
            else:
                self.button.description = 'Pull image'
            self.button.style.font_weight = '400'
            self.button.style.button_color = '#9feeb2'


    def _set_status_value(self):
        from docker import errors

        if self._client is None:
            self.status.value = 'n/a'
        else:
            try:
                imginfo = self._client.inspect_image(self.image)
            except errors.ImageNotFound:
                if self._err:
                    self.status.value = WARNING
                else:
                    self.status.value = MISSING
            else:
                self.status.value = INSTALLED

    def _watch_pull_logs(self, stream):
        found = set()
        inprogress = set()
        done = set()
        for item in stream:
            if 'errorDetail' in item or 'error' in item:
                self.msg.value = item
                self._err = True
            elif 'status' in item and 'id' in item:  # for pulling images
                imgid = item['id']
                found.add(imgid)
                stat = item['status'].strip()
                fields = stat.split()

                if fields[0:2] in (['Pull','complete'], ['Already','exists']):
                    done.add(imgid)
                    self.msg.value = 'Pulling from repository: %s/%s layers complete' % (len(done), len(found))
                elif fields[0] in ('Pulling','Extracting', 'Downloading'):
                    inprogress.add(imgid)
