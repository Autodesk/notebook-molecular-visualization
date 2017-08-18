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
import ipywidgets as ipy
import moldesign as mdt

MISSING = u'\u274C'
INSTALLED = u"\u2705"
WARNING = u"⚠️"


class DockerImageStatus(ipy.VBox):
    def __init__(self):

        images = self._get_images()
        self.header = ipy.HTML(
                '<span class="nbmolviz-table-header" style="width:950px"">Image status</span>',
                layout=ipy.Layout(align_items='flex-end'))
        super().__init__([self.header] + [DockerImageView(im) for im in sorted(images)])

    def _get_images(self):
        return set(p.get_docker_image_path()
                   for p in mdt.compute.packages.executables + mdt.compute.packages.packages)


class DockerImageView(ipy.HBox):
    LOADER = "<div class='loader' />"

    def __init__(self, image):
        self._err = False
        self.image = image
        self.status = ipy.HTML(layout=ipy.Layout(width="20px"))
        self.html = ipy.HTML(value=image, layout=ipy.Layout(width="400px"))
        self.html.add_class('nbmolviz-monospace')
        self.msg = ipy.HTML(layout=ipy.Layout(width='300px'))
        if mdt.compute.config.devmode:
            self.button = ipy.Button(description='Rebuild', layout=ipy.Layout(width='100px'))
            self.button.on_click(self.rebuild)
        else:
            self.button = ipy.Button(description='Pull', layout=ipy.Layout(width='100px'))
            self.button.on_click(self.pull)
        self._client = mdt.compute.get_engine().client
        self._set_status_value()
        super().__init__(children=[self.status, self.html, self.button, self.msg])

    def pull(self, *args):
        thread = threading.Thread(target=self._run_pull)
        thread.start()

    def rebuild(self, *args):
        raise NotImplementedError("You'll need to do this manually ...")

    def _run_pull(self):
        from docker import errors
        try:
            self.button.disabled = True
            self._err = False
            self.status.value = self.LOADER
            self.msg.value = 'Starting pull ...'

            try:
                response = self._client.pull(self.image, stream=True, decode=True)
                self._watch_pull_logs(response)
            except errors.NotFound as exc:
                self._err = True
                self.msg.value = 'ERROR: %s' % exc.explanation

        finally:
            self._set_status_value()
            self.button.disabled = False
            if not self._err:
                self.msg.value = 'Pull successful.'

    def _set_status_value(self):
        from docker import errors

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
