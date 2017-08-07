""" Unfortunately, the tests here do not yet test the visualizations themselves, merely
the supporting functionality
"""
from past.builtins import unicode

import pytest

from moldesign._tests.molecule_fixtures import *
from nbmolviz.utils import translate_color


def test_color_translation():
    css_color = 'tomato'
    translated_color = translate_color(css_color)
    assert translated_color == '0xff6347'


@pytest.fixture
def wfn_viewer(h2_rhf_augccpvdz):
    return h2_rhf_augccpvdz.draw_orbitals()


def test_generate_orbgrid_works(wfn_viewer):
    wfn_viewer.numpoints = 64
    grid, values = wfn_viewer._calc_orb_grid(wfn_viewer.mol.wfn.orbitals.canonical[1])
    assert grid.xpoints == grid.ypoints == grid.zpoints == 64


def test_generating_cubefile_works(wfn_viewer):
    wfn_viewer.numpoints = 64
    grid, values = wfn_viewer._calc_orb_grid(wfn_viewer.mol.wfn.orbitals.canonical[1])
    cb = wfn_viewer._grid_to_cube(grid, values)
    assert isinstance(cb, unicode)
