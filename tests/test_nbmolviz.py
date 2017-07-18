""" Unfortunately, the tests here do not yet test the visualizations themselves, merely
the supporting functionality
"""
import io
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
    grid, values = wfn_viewer.calc_orb_grid(0, 64, 0)
    assert grid.xpoints == grid.ypoints == grid.zpoints == 64


def test_generating_cubefile_works(wfn_viewer):
    cb = wfn_viewer.get_cubefile(0, 64, 0)
    assert isinstance(cb, str)

