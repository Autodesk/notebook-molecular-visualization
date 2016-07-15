# Adapted from https://github.com/jupyter/widget-cookiecutter

from __future__ import print_function

import os
import sys
import versioneer
from setuptools import setup, find_packages, Command
from setuptools.command.egg_info import egg_info
from subprocess import check_call

from distutils import log

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])
here = os.path.dirname(os.path.abspath(__file__))

PACKAGE_NAME = 'nbmolviz'
KEYWORDS = 'jupyter notebook chemistry widget 3D visualization'.split()
LONG_DESCRIPTION = 'Molecular visualization in Jupyter notebooks'
CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Science/Research
Intended Audience :: Developers
Intended Audience :: Education
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
Topic :: Scientific/Engineering :: Chemistry
Topic :: Scientific/Engineering :: Visualization
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
""".splitlines()

assert sys.version_info[:2] == (2, 7), "Sorry, this package requires Python 2.7."

with open('requirements.txt', 'r') as reqfile:
    requirements = [x.strip() for x in reqfile if x.strip()]

PYEXT = set('.py .pyc .pyo'.split())

###################################################################
#   Set up versioning   (using versioneer)                        #
###################################################################
versioncmds = versioneer.get_cmdclass()
build_py = versioncmds['build_py']
sdist = versioncmds['sdist']


###################################################################
#   NPM setup and command decorators                              #
###################################################################
node_root = os.path.join(here, 'js')
is_repo = os.path.exists(os.path.join(here, '.git'))

npm_path = os.pathsep.join([
    os.path.join(node_root, 'node_modules', '.bin'),
    os.environ.get('PATH', os.defpath),
])

def update_package_data(distribution):
    """update package_data to catch changes during setup"""
    build_py = distribution.get_command_obj('build_py')
    # distribution.package_data = find_package_data()
    # re-init build_py options which load package_data
    build_py.finalize_options()


def js_prerelease(command, strict=False):
    """decorator for building minified js/css prior to another command"""
    class DecoratedCommand(command):
        def run(self):
            jsdeps = self.distribution.get_command_obj('jsdeps')
            if not is_repo and all(os.path.exists(t) for t in jsdeps.targets):
                # sdist, nothing to do
                command.run(self)
                return

            try:
                self.distribution.run_command('jsdeps')
            except Exception as e:
                missing = [t for t in jsdeps.targets if not os.path.exists(t)]
                if strict or missing:
                    log.warn('rebuilding js and css failed')
                    if missing:
                        log.error('missing files: %s' % missing)
                    raise e
                else:
                    log.warn('rebuilding js and css failed (not a problem)')
                    log.warn(str(e))
            command.run(self)
            update_package_data(self.distribution)
    return DecoratedCommand


class NPM(Command):
    description = 'install package.json dependencies using npm'

    user_options = []

    node_modules = os.path.join(node_root, 'node_modules')

    targets = [
        os.path.join(here, 'nbmolviz', 'static', 'extension.js'),
        os.path.join(here, 'nbmolviz', 'static', 'index.js')
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def has_npm(self):
        try:
            check_call(['npm', '--version'])
            return True
        except:
            return False

    def should_run_npm_install(self):
        package_json = os.path.join(node_root, 'package.json')
        node_modules_exists = os.path.exists(self.node_modules)
        return self.has_npm()

    def run(self):
        has_npm = self.has_npm()
        if not has_npm:
            log.error("`npm` unavailable.  If you're running this command using sudo, make sure `npm` is available to sudo")

        env = os.environ.copy()
        env['PATH'] = npm_path

        if self.should_run_npm_install():
            log.info("Installing build dependencies with npm.  This may take a while...")
            check_call(['npm', 'install'], cwd=node_root, stdout=sys.stdout, stderr=sys.stderr)
            os.utime(self.node_modules, None)

        for t in self.targets:
            if not os.path.exists(t):
                msg = 'Missing file: %s' % t
                if not has_npm:
                    msg += '\nnpm is required to build a development version of widgetsnbextension'
                raise ValueError(msg)

        # update package data in case this created new files
        update_package_data(self.distribution)


###################################################################
#   Actual setup command                                          #
###################################################################

args = dict(
        name=PACKAGE_NAME,
        version=versioneer.get_version(),
        packages=find_packages(),
        classifiers=CLASSIFIERS,
        url='http://moldesign.bionano.autodesk.com/',
        license='Apache 2.0',
        include_package_data=True,
        cmdclass={
            'build_py': js_prerelease(build_py),
            'egg_info': js_prerelease(egg_info),
            'sdist': js_prerelease(sdist, strict=True),
            'jsdeps': NPM},
        data_files=[
                ('share/jupyter/nbextensions/nbmolviz-js', [
                    'nbmolviz/static/extension.js',
                    'nbmolviz/static/index.js',
                    'nbmolviz/static/index.js.map',
                ]),
            ],
        install_requires=requirements,
        author='Autodesk, Inc.',
        author_email='aaron.virshup [at] autodesk [dot] com',
        description='The Notebook Molecular Visualization Library: '
                    'WebGL-based molecular visualization '
                    'tools for Jupyter notebooks',
        keywords=KEYWORDS
)

setup(**args)
