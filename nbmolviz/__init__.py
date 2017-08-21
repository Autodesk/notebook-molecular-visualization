from __future__ import print_function
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
import os as _os

# package metadata
from . import _version
__version__ = _version.get_versions()['version']
__copyright__ = "Copyright 2017 Autodesk Inc."
__license__ = "Apache 2.0"

PACKAGE_PATH = _os.path.dirname(_os.path.abspath(__file__))


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'nbmolviz-js',
        'require': 'nbmolviz-js/extension'
    }]


def find_static_assets():
    from warnings import warn
    warn("""To use the nbmolviz-js nbextension, you'll need to update
    the Jupyter notebook to version 4.2 or later.""")
    return []

