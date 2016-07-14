notebook-molecular-visualization
===============================

A Python widgets library for 2D and 3D molecular visualization in Jupyter notebooks

## Installation

    $ pip install nbmolviz
    $ jupyter nbextension enable --python --system nbmolviz
    $ jupyter nbextension enable --python --system widgetsnbextension



## Examples

To draw an OpenBabel molecule:
```python
import nbmolviz
import pybel
benzene = pybel.read_string('smi','c1cccc1').next()
nbmolviz.visualize(benzene)
```



## Dev install
Requires npm.

    $ git clone https://github.com/autodesk/notebook-molecular-visualization.git
    $ cd notebook-molecular-visualization/nbmolviz
    $ python setup.py jsdeps
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --user nbmolviz
    $ jupyter nbextension enable --py --user nbmolviz
    
This will build your widgets into a folder at `notebook-molecular-visualization/nbmolviz/static`

During development, to see the effects of changes to any javascript files (in notebook-molecular/visualization/js/src), run `python setup.py jsdeps` and reload any notebook browser windows.


## Contributing

This project is developed and maintained by the [Molecular Design Toolkit](https://github.com/autodesk/molecular-design-toolkit) project. Please see that project's [CONTRIBUTING document](https://github.com/autodesk/molecular-design-toolkit/CONTRIBUTING.md) for details.


## About
This package started life as hackathon project for the <a href="http://www.cecam.org/workshop-1214.html">CECAM 2015 Macromolecular Simulation Workshop.</a> It's since undergone a complete source rewrite, and is being released by BioNano Research at Autodesk as part of our suite of Molecular Design Tools.

The visualizers offered by this library were built using:
  - <a href="https://github.com/jupyter/ipywidgets">ipywidgets</a> - UI library for interactivity in Jupyter notebooks
  - <a href="http://3dmol.csb.pitt.edu/doc/index.html">3Dmol.js</a> - 3D molecular visualization library for web browsers
  - <a href="http://d3js.org/">D3.js</a> - javascript library for graph visualization



## License

Copyright 2016 Autodesk Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.