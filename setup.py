import os
import sys
from os.path import relpath, join
from setuptools import find_packages, setup
from setuptools.command.install import install
import versioneer

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

def find_package_data():
    files = []
    for root, dirnames, filenames in os.walk('nbmolviz'):
        for fn in filenames:
            basename, fext = os.path.splitext(fn)
            if fext not in PYEXT:
                files.append(relpath(join(root, fn), 'nbmolviz'))
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
    name='Notebook Molecular Visualization Library',
    version=versioneer.get_version(),
    packages=find_packages(),
    classifiers=CLASSIFIERS.split('\n'),
    url='http://autodeskresearch.com',
    license='Apache 2.0',
    cmdclass=cmdclass,
    package_data={'nbmolviz': find_package_data()},
    install_requires=requirements,
    author='Autodesk BioNano Research',
    author_email='aaron.virshup [at] autodesk [dot] com',
    description='WebGL-based molecular visualization tools for Jupyter notebooks'
)

