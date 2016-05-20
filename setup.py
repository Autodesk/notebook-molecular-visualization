import os
import sys
from os.path import relpath, join
from setuptools import find_packages, setup
from setuptools.command.install import install
import versioneer

PACKAGE_NAME = 'nbmolviz'

assert sys.version_info[:2] == (2, 7), "Sorry, this package requires Python 2.7."


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
"""

PYEXT = set('.py .pyc .pyo'.split())

with open('requirements.txt', 'r') as reqfile:
    requirements = [x.strip() for x in reqfile if x.strip()]


def find_package_data(pkgdir):
    """ Just include all files that won't be included as package modules.
    """
    files = []
    for root, dirnames, filenames in os.walk(pkgdir):
        not_a_package = '__init__.py' not in filenames
        for fn in filenames:
            basename, fext = os.path.splitext(fn)
            if not_a_package or (fext not in PYEXT) or ('static' in fn):
                files.append(relpath(join(root, fn), pkgdir))
    return files


class PostInstall(install):
    def run(self):
        install.run(self)
        self.post_install()

    def post_install(self):
        from nbmolviz import install
        install.widgets()

cmdclass = versioneer.get_cmdclass()
cmdclass['install'] = PostInstall

setup(
    name=PACKAGE_NAME,
    version=versioneer.get_version(),
    packages=find_packages(),
    classifiers=CLASSIFIERS.split('\n'),
    url='http://autodeskresearch.com',
    license='Apache 2.0',
    cmdclass=cmdclass,
    package_data={PACKAGE_NAME: find_package_data(PACKAGE_NAME)},
    install_requires=requirements,
    author='Autodesk BioNano Research',
    author_email='aaron.virshup [at] autodesk [dot] com',
    description='The Notebook Molecular Visualization Library: WebGL-based molecular visualization '
                'tools for Jupyter notebooks'
)

