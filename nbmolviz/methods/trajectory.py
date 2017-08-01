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


def draw3d(traj, **kwargs):
    """TrajectoryViewer: create a trajectory visualization

    Args:
        **kwargs (dict): kwargs for :class:`moldesign.widgets.trajectory.TrajectoryViewer`
    """
    from ..viewers.trajectory_viewer import TrajectoryViewer
    traj._viz = TrajectoryViewer(traj, **kwargs)
    return traj._viz
draw = draw3d  # synonym for backwards compatibility


def draw_orbitals(traj, align=True, **kwargs):
    """ Visualize trajectory with molecular orbitals

    Args:
        align (bool): Align orbital phases (i.e., multiplying by -1 as needed) to prevent sign
           flips between frames

    Returns:
        TrajectoryOrbViewer: create a trajectory visualization
    """
    from ..viewers.trajectory_viewer import TrajectoryOrbViewer

    for frame in traj:
        if 'wfn' not in frame:
            raise ValueError("Can't draw orbitals - orbital information missing in at least "
                             "one frame. It must be calculated with a QM method.")

    if align:
        traj.align_orbital_phases()
    traj._viz = TrajectoryOrbViewer(traj, **kwargs)
    return traj._viz


def plot(traj, x, y, **kwargs):
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
        x = getattr(traj, x)
        xl = '%s / %s' % (strx, getattr(x, 'units', 'dimensionless'))
    if type(y) is str:
        stry = y
        y = getattr(traj, y)
        yl = '%s / %s' % (stry, getattr(y, 'units', 'dimensionless'))
    plt = pylab.plot(x, y, **kwargs)
    pylab.xlabel(xl); pylab.ylabel(yl); pylab.grid()
    return plt
