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

import sys
import argparse

class SmartFormatter(argparse.HelpFormatter):
    """
    From https://stackoverflow.com/a/22157136/1958900
    """
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

def main():
    from . import install, _version
    parser = argparse.ArgumentParser('python -m nbmolviz', formatter_class=SmartFormatter)

    parser.add_argument('command', choices=['activate', 'uninstall', 'check'],
                        help='R|activate - install and enable nbmolviz\n'
                        'uninstall - remove old nbmolviz installations\n'
                        'check - check installed versions\n')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--sys-prefix', '--env', '--venv', action='store_true',
                        help="Apply command to your virtual environment")
    group.add_argument('--user', action='store_true',
                        help="Apply command to all of this user's environments")
    group.add_argument('--sys', '--global', '--system', action='store_true',
                        help="Apply command to the global system configuration")

    args = parser.parse_args()

    if args.command == 'check':
        print('Expected version:', _version.get_versions()['version'])
        versions = install.get_installed_versions('nbmolviz-js', True)
        foundone = False
        for key, vers in versions.items():
            if vers.installed:
                if foundone:
                    print('--')
                else:
                    foundone = True
                    print('Installed notebook extension locations:\n')

                if key == 'user':
                    print('Environment:', 'current user')
                elif key == 'environment':
                    print('Environment:', 'current virtual environment')
                else:
                    assert key == 'system'
                    print('Environment:', 'global / system-wide')

                print('Version: ', vers.version)
                print('Location: ', vers.path)

        if not foundone:
            print("NBMolViz Jupyter extensions are not installed in any current environments")

    elif args.command == 'activate':
        if not (args.sys_prefix or args.user or args.sys):
            install.autoinstall()

        if args.sys_prefix:
            install.activate('--sys-prefix')
        if args.user:
            install.activate('--user')
        if args.sys:
            install.activate('--system')

    elif args.command == 'uninstall':
        if not (args.sys_prefix or args.user or args.sys):
            args.sys_prefix = args.user = args.sys = True

        if args.sys_prefix:
            install.uninstall('--sys-prefix')
        if args.user:
            install.uninstall('--user')
        if args.sys:
            install.uninstall('--system')

    else:
        assert False, "parser failure"


if __name__ == '__main__':
    main()