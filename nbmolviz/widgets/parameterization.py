# Copyright 2016 Autodesk Inc.
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
""" This module contains methods to display 3D information about the assignment of force field
parameters to a biomolecule.

This helps users to visualize errors that occur when trying to assign a forcefield,
such as unrecognized residues, missing atoms, etc.

NOTE:
    This is currently tied to ambertools and tleap! It will need to be made generic if/when
    another method for assigning forcefields is added.
"""
import collections

import ipywidgets as ipy

from moldesign import uibase
from moldesign import utils


def show_parameterization_results(errormessages, molin, molout=None):
    if uibase.widgets_enabled:
        report = ParameterizationDisplay(errormessages, molin, molout)
        uibase.display_log(report, title='ERRORS/WARNINGS', show=True)

    else:
        print 'Forcefield assignment: %s' % ('Success' if molout is not None else 'Failure')
        for err in errormessages:
            print utils.html_to_text(err.desc)



class ParameterizationDisplay(ipy.Box):
    def __init__(self, errormessages, molin, molout=None):
        self.molin = molin
        self.molout = molout
        self.msg = errormessages

        self.status = ipy.HTML('<h4>Forcefield assignment: %s</h4>' %
                               ('Success' if molout else 'FAILED'))

        self.listdesc = ipy.HTML('<b>Errors / warnings:</b>')
        error_display = collections.OrderedDict((e.short, e) for e in self.msg)
        if len(error_display) == 0:
            error_display['No errors or warnings.'] = StructureOk()
        self.errorlist = ipy.Select(options=error_display)
        self.errmsg = ipy.HTML('-')

        self.viewer = self.molin.draw3d()
        self.viewer.ribbon(opacity=0.7)

        if self.errorlist.value is not None:
            self.switch_display({'old': self.errorlist.value, 'new': self.errorlist.value})
        self.errorlist.observe(self.switch_display, 'value')
        children = (self.status,
                    ipy.HBox([self.viewer, ipy.VBox([self.listdesc, self.errorlist])]),
                    self.errmsg)

        super(ParameterizationDisplay, self).__init__(children=children,
                                                      layout=ipy.Layout(display='flex',
                                                                        flex_flow='column'))


    def switch_display(self, d):
        old = d['old']
        old.unshow(self.viewer)
        self.errmsg.value = '-'
        new = d['new']
        new.show(self.viewer)
        self.errmsg.value = new.desc
