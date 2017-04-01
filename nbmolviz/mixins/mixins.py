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

from moldesign import data, utils

from .. import widgets as mdtwidgets


class ResidueNotebookMixin(object):
    """ Mixin class for Residues with notebook-relevenat classes
    """

    def _repr_markdown_(self):
        return self.markdown_summary()

    def markdown_summary(self):
        """ Markdown-formatted information about this residue

        Returns:
            str: markdown-formatted string
        """
        if self.type == 'placeholder':
            return '`%s`' % repr(self)

        if self.molecule is None:
            lines = ["<h3>Residue %s</h3>" % self.name]
        else:
            lines = ["<h3>Residue %s (index %d)</h3>" % (self.name, self.index)]

        if self.type == 'protein':
            lines.append('**Residue codes**: %s / %s' % (self.resname, self.code))
        else:
            lines.append("**Residue code**: %s" % self.resname)
        lines.append('**Type**: %s' % self.type)
        if self.resname in data.RESIDUE_DESCRIPTIONS:
            lines.append('**Description**: %s' % data.RESIDUE_DESCRIPTIONS[self.resname])

        lines.append('**<p>Chain:** %s' % self.chain.name)

        lines.append('**PDB sequence #**: %d' % self.pdbindex)

        terminus = None
        if self.type == 'dna':
            if self.is_3prime_end:
                terminus = "3' end"
            elif self.is_5prime_end:
                terminus = "5' end"
        elif self.type == 'protein':
            if self.is_n_terminal:
                terminus = 'N-terminus'
            elif self.is_c_terminal:
                terminus = 'C-terminus'
        if terminus is not None:
            lines.append('**Terminal residue**: %s of chain %s' % (terminus, self.chain.name))

        if self.molecule is not None:
            lines.append("**Molecule**: %s" % self.molecule.name)

        lines.append("**<p>Number of atoms**: %s" % self.num_atoms)
        if self.backbone:
            lines.append("**Backbone atoms:** %s" % ', '.join(x.name for x in self.backbone))
            lines.append("**Sidechain atoms:** %s" % ', '.join(x.name for x in self.sidechain))
        else:
            lines.append("**Atom:** %s" % ', '.join(x.name for x in self.atoms))

        return '<br>'.join(lines)



class TrajNotebookMixin(object):
    @utils.kwargs_from(mdtwidgets.trajectory.TrajectoryViewer)
    def draw3d(self, **kwargs):
        """TrajectoryViewer: create a trajectory visualization

        Args:
            **kwargs (dict): kwargs for :class:`moldesign.widgets.trajectory.TrajectoryViewer`
        """
        self._viz = mdtwidgets.trajectory.TrajectoryViewer(self, **kwargs)
        return self._viz
    draw = draw3d  # synonym for backwards compatibility

    def draw_orbitals(self, align=True):
        """ Visualize trajectory with molecular orbitals

        Args:
            align (bool): Align orbital phases (i.e., multiplying by -1 as needed) to prevent sign
               flips between frames

        Returns:
            TrajectoryOrbViewer: create a trajectory visualization
        """
        for frame in self:
            if 'wfn' not in frame:
                raise ValueError("Can't draw orbitals - orbital information missing in at least "
                                 "one frame. It must be calculated with a QM method.")

        if align: self.align_orbital_phases()
        self._viz = mdtwidgets.trajectory.TrajectoryOrbViewer(self)
        return self._viz

    def plot(self, x, y, **kwargs):
        """ Create a matplotlib plot of property x against property y

        Args:
            x,y (str): names of the properties
            **kwargs (dict): kwargs for :meth:`matplotlib.pylab.plot`

        Returns:
            List[matplotlib.lines.Lines2D]: the lines that were plotted

        """
        from matplotlib import pylab
        xl = yl = None
        if type(x) is str:
            strx = x
            x = getattr(self, x)
            xl = '%s / %s' % (strx, x.units)
        if type(y) is str:
            stry = y
            y = getattr(self, y)
            yl = '%s / %s' % (stry, y.units)
        plt = pylab.plot(x, y, **kwargs)
        pylab.xlabel(xl); pylab.ylabel(yl); pylab.grid()
        return plt