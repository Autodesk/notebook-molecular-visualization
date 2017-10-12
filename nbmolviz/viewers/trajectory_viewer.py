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
import traitlets

from ..viewers import ViewerContainer
from ..widget_utils import process_widget_kwargs
from ..widgets.components import AtomInspector
from ..uielements.components import HBox, VBox


class TrajectoryViewer(ViewerContainer):
    """ 3D representation, with animation controls, for a trajectory.

    Users will typically instantiate this using ``trajectory.draw()``

    Args:
        display (bool): immediately display this to the notebook (default: False)
        **kwargs (dict): keyword arguments for :class:`ipywidgets.Box`
    """

    current_frame = traitlets.Integer(0).tag(sync=True)

    def __init__(self, trajectory, display=False, **kwargs):
        from IPython.display import display as displaynow

        self.playbar = None
        self.playbutton = None
        self.slider = None
        self.viewer = None
        self.annotation = None

        self.traj = trajectory
        trajectory._apply_frame(trajectory.frames[0])
        self.viewcontainer = self._get_viewer_container()
        self.viewer.show_unbonded()
        self.controls = self.make_controls()
        self.pane = VBox(children=(self.viewcontainer, self.controls))

        super().__init__(children=(self.pane, AtomInspector(self.traj.mol)),
                         viewer=self.viewcontainer, **process_widget_kwargs(kwargs))

        self.show_frame(self.current_frame)
        if display:
            displaynow(self)

    def _get_viewer_container(self):
        """ This is treated differently in sublcasses, which is
        why it's factored out
        """
        self.viewer = self.traj._tempmol.draw3d(style='licorice')
        return self.viewer

    @property
    def wfn(self):
        return self.trajectory.wfn[self.current_frame]

    def show_frame(self, framenum):
        self.annotation.value = self.traj.frames[framenum].get('annotation', '')
        self.viewer.set_positions(self.traj.positions[framenum])
        self.readout.value = '%s / %s' % (framenum, self.traj.num_frames - 1)
        self.current_frame = framenum

    def make_controls(self):
        self.playbutton = ipy.Play(value=0,
                                   min=0,
                                   max=self.traj.num_frames-1)

        self.slider = ipy.IntSlider(value_selects='framenum', value=0,
                                    description='Frame:', min=0, max=len(self.traj)-1,
                                    readout=False)
        self.readout = ipy.HTML(value='/%d' % (self.traj.num_frames - 1))
        self.annotation = ipy.HTML()

        traitlets.link((self.playbutton, 'value'), (self.slider, 'value'))
        traitlets.link((self.slider, 'value'), (self, 'current_frame'))
        self.playbar = HBox((self.playbutton, self.slider, self.readout))
        return VBox((self.annotation, self.playbar))

    @traitlets.observe('current_frame')
    def _change_frame(self, change):
        self.show_frame(change['new'])

    def __getattr__(self, item):
        """Users can run viz commands directly on the trajectory,
        e.g., trajectory.cpk(atoms=mol.chains['B'])"""
        # TODO: modify __dir__ to match
        return getattr(self.viewer, item)


class TrajectoryOrbViewer(TrajectoryViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._caching = False
        self.cache_orbital_button = ipy.Button()
        self.cache_orbital_button.on_click(self.cache_orbitals)
        self.viewcontainer.observe(self.handle_orb_update, 'current_orbital')
        self.pane.children += (self.cache_orbital_button,)
        self.handle_orb_update({'new':None})

    def show_frame(self, framenum):
        wfn = self.traj.frames[framenum].wfn
        self.viewcontainer.wfn = wfn

        with self.hold_trait_notifications(), \
             self.viewcontainer.orblist.hold_sync(), \
             self.viewcontainer.hold_trait_notifications(), \
             self.viewcontainer.viewer.hold_trait_notifications(), \
             self.viewcontainer.viewer.hold_sync():

            super().show_frame(framenum)
            self.viewcontainer.new_orb_type()

    def cache_orbitals(self, *args):
        import threading
        self.cache_orbital_button.disabled = True
        self._caching = True
        threading.Thread(target=self._cache_orbital_thread).start()

    def _cache_orbital_thread(self):
        try:
            self.cache_orbital_button.button_style = 'info'
            self.enable_controls(False)
            for fnum in range(self.traj.num_frames):
                self.cache_orbital_button.description = 'Calculating frame %d' % fnum
                self.show_frame(fnum)
        except Exception:
            self.cache_orbital_button.description = 'Orbital calc failed'
            self.cache_orbital_button.button_style = 'warning'
            self.cache_orbital_button.disabled = False
            raise
        else:
            self.cache_orbital_button.description = 'Animation ready.'
            self.cache_orbital_button.button_style = 'success'
            self.cache_orbital_button.disabled = True
        finally:
            self.enable_controls(True)
            self._caching = False

    def handle_orb_update(self, change):
        if self._caching:
            return
        if change['new'] is None:
            self.cache_orbital_button.description = '--'
            self.cache_orbital_button.button_style = ''
            self.cache_orbital_button.disabled = True
            self.playbutton.interval = 100
        elif change['old'] != change['new']:
            self.cache_orbital_button.description = 'Prep animation'
            self.cache_orbital_button.button_style = 'primary'
            self.cache_orbital_button.disabled = False
            self.playbutton.interval = 500

    def enable_controls(self, enabled):
        self.viewcontainer.orblist.disabled = not enabled
        self.viewcontainer.type_dropdown.disabled = not enabled
        self.slider.disabled = not enabled
        self.playbutton.disabled = not enabled

    def _get_viewer_container(self):
        orbviewer = self.traj._tempmol.draw_orbitals()
        self.viewer = orbviewer.viewer
        return orbviewer


class FrameInspector(ipy.HTML):
    framenum = traitlets.Integer(0)

    def __init__(self, traj, **kwargs):
        self.traj = traj
        super().__init__(**process_widget_kwargs(kwargs))

    @traitlets.observe('framenum')
    def update_frame_data(self, change):
        framenum = change['new']

        if hasattr(self.traj.frames[framenum], 'time') and self.traj.frames[framenum].time is not None:
            result = 'Time: %s; ' % self.traj.frames[framenum].time.defunits()
        else:
            result = ''

        try:
            result += self.traj.frames[framenum].annotation
        except (KeyError, AttributeError):
            pass

        self.value = result
