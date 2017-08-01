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
from past.builtins import basestring

from ..base.base_widget import MessageWidget
from moldesign import utils
from .. import colormaps


class BaseViewer(MessageWidget):
    def colormap(self, atomvalues, atoms=None, mplmap='auto', categorical=None, save=True):
        """ Color atoms according to categorical or numeric data

        Args:
            atomvalues (callable OR list or str): Either:
              - a callable that takes an atom and the data,
              - a list of values of each atom
              - the name of an atomic property (e.g., 'residue' or 'mass')
            atoms (moldesign.molecules.AtomContainer): atoms to color (default: self.mol.atoms)
            mplmap (str): name of the matplotlib colormap to use if colors aren't explicitly
               specified)
            categorical (bool): If None (the default), automatically detect whether the
               data is categorical or numerical. Otherwise, use this flag to force
               interpretation of the data as categorical (True) or numerical (False)
            save (bool): permanently color theses atoms this way (until self.unset_color is called)


        Returns:
            dict: mapping of categories to colors
        """
        atoms = utils.if_not_none(atoms, self.mol.atoms)
        if isinstance(atomvalues, basestring):
            # shortcut to use strings to access atom attributes, i.e. "ff.partial_charge"
            attrs = atomvalues.split('.')
            atomvalues = []
            for atom in atoms:
                obj = atom
                for attr in attrs:
                    obj = getattr(obj, attr)
                atomvalues.append(obj)

        elif callable(atomvalues):
            atomvalues = list(map(atomvalues, atoms))

        colors = colormaps.colormap(atomvalues, mplmap=mplmap, categorical=categorical)
        self.set_colors(colors, atoms=atoms, save=save)

        return {v:c for v,c in zip(atomvalues, colors)}

    color_by = colormap