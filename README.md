notebook-molecular-visualization
===============================

A Python widgets library for 2D and 3D molecular visualization in Jupyter notebooks

Installation
------------

To install use pip:

    $ pip install nbmolviz
    $ jupyter nbextension enable --py --sys-prefix nbmolviz


For a development installation (requires npm),

    $ git clone https://github.com/autodesk/notebook-molecular-visualization.git
    $ cd nbmolviz
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --user nbmolviz
    $ jupyter nbextension enable --py --user nbmolviz

##About
This package started life as hackathon project for the <a href="http://www.cecam.org/workshop-1214.html">CECAM 2015 Macromolecular Simulation Workshop.</a> It's since undergone a complete source rewrite, and is being released by BioNano Research at Autodesk as part of our suite of Molecular Design Toolks.

##Dependencies
This package is designed for the Jupyter Notebook platform and requires the ```ipython[notebook]``` and ```ipywidgets``` packages.

*Inclusions
- This packages uses the 3DMol.js library as a backend for molecular visualization - a minified version is included here. See <a href="http://3dmol.csb.pitt.edu/doc/index.html">3DMol.js</a>
- Several functions dealing with wavefunction math were derived from <a href="https://github.com/rpmuller/pyquante2">the PyQuante2 source code</a>.