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
import os
from notebook.nbextensions import install_nbextension
import nbmolviz

PKGPATH = nbmolviz.__path__[0]


def widgets(overwrite=True):
    """Install the widgets. This isn't actually used, for now - we just load them
    the nbmolviz directory"""
    install_nbextension(os.path.join(PKGPATH, 'static'),
                        destination='molviz',
                        overwrite=overwrite)

def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="nbmolvizjs",
        # _also_ in the `nbextension/` namespace
        require="my_fancy_module/index")]


if __name__ == '__main__':
    widgets()
