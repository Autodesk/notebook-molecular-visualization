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

import ipywidgets as ipy

import moldesign as mdt
from ..uielements import StyledTab
from ..uielements.components import HBox, VBox



def configure():
    from IPython.display import display
    display(MDTConfig())

MISSING = u'\u274C'
INSTALLED = u"\u2705"


class MDTConfig(VBox):
    def __init__(self):
        from .docker import DockerConfig
        from .interfaces import InterfaceStatus
        from .visualization import MdtExtensionConfig

        self.interface_status = InterfaceStatus()
        self.compute_config = DockerConfig()
        self.nbextension_config = MdtExtensionConfig()
        self.changelog = ChangeLog()
        self.tab_list = StyledTab([ipy.Box(),
                                   self.nbextension_config,
                                   self.interface_status,
                                   self.compute_config,
                                   self.changelog])
        self.tab_list.set_title(0, '^')
        self.tab_list.set_title(1, 'Notebook config')
        self.tab_list.set_title(2, "Interfaces")
        self.tab_list.set_title(3, 'Docker config')
        self.tab_list.set_title(4, "What's new")
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


class ChangeLog(ipy.Box):
    def __init__(self):
        from pip._vendor.packaging import version

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
        from pip._vendor.packaging import version
        import xmlrpc.client
        pypi = xmlrpc.client.ServerProxy('https://pypi.python.org/pypi')
        return version.parse(pypi.package_releases('moldesign')[0])

