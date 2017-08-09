from __future__ import print_function
from future.builtins import *
from future.standard_library import install_aliases
install_aliases()

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

from moldesign import utils
from ..uielements.components import VBox
from . import GeometryViewer


class ViewerContainer(VBox):
    """
    Container for one or more viewers. Delegates calls to the component viewers
    """
    def __reduce__(self):
        """These don't gat passed around,
        so it reduces to NOTHING"""
        return utils.make_none, tuple()

    def __init__(self, children, viewer=None, graphviewer=None, **kwargs):
        if 'layout' not in kwargs:
            kwargs['layout'] = ipy.Layout(flex_flow='column', width='100%')
        super().__init__(children=children, **kwargs)
        self.viewer = viewer
        self.graphviewer = graphviewer


    @utils.args_from(GeometryViewer.set_color)
    def set_color(self, *args, **kwargs):
        if self.graphviewer: self.graphviewer.set_color(*args, **kwargs)
        if self.viewer: self.viewer.set_color(*args, **kwargs)

    @utils.args_from(GeometryViewer.set_color)
    def color_by(self, *args, **kwargs):
        if self.graphviewer: self.graphviewer.color_by(*args, **kwargs)
        if self.viewer: self.viewer.color_by(*args, **kwargs)

    @utils.args_from(GeometryViewer.set_color)
    def set_colors(self, *args, **kwargs):
        if self.graphviewer: self.graphviewer.set_colors(*args, **kwargs)
        if self.viewer: self.viewer.set_colors(*args, **kwargs)

    @utils.args_from(GeometryViewer.unset_color)
    def unset_color(self, *args, **kwargs):
        if self.graphviewer: self.graphviewer.unset_color(*args, **kwargs)
        if self.viewer: self.viewer.unset_color(*args, **kwargs)

    def __getattr__(self, item):
        if item != 'viewer' and self.viewer is not None:
            return getattr(self.viewer, item)
        else:
            raise AttributeError(item)

