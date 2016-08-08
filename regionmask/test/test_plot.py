import numpy as np

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from regionmask import Regions_cls, Region_cls, _subsample

from shapely.geometry import Polygon, MultiPolygon

from pytest import raises

# =============================================================================

# set up the testing regions

name = 'Example'
numbers = [0, 1]
names = ['Unit Square1', 'Unit Square2']
abbrevs = ['uSq1', 'uSq2']

outl1 = ((0, 0), (0, 1), (1, 1.), (1, 0))
outl2 = ((0, 1), (0, 2), (1, 2.), (1, 1))
outlines = [outl1, outl2]

r1 = Regions_cls(name, numbers, names, abbrevs, outlines)

numbers = [1, 2]
names = {1:'Unit Square1', 2: 'Unit Square2'}
abbrevs = {1:'uSq1', 2:'uSq2'}
poly1 = Polygon(outl1)
poly2 = Polygon(outl2)
poly = {1: poly1, 2: poly2}

r2 = Regions_cls(name, numbers, names, abbrevs, poly)    

# =============================================================================

def test__subsample():
    lon, lat = _subsample([[0, 1], [1, 0]])
    res = np.concatenate((np.linspace(1, 0), np.linspace(0, 1)))
    assert np.allclose(lon, res)

# =============================================================================

def test_plot_lines():
    ax = r1.plot(subsample=False)

    lines = ax.lines

    assert len(lines) == 2

    assert np.allclose(ax.lines[0].get_xydata(), outl1)
    assert np.allclose(ax.lines[1].get_xydata(), outl2)
    
    plt.close('all')


def test_plot_lines_subsample():
    
    ax = r1.plot(subsample=True)
    lines = ax.lines

    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata().shape, (200, 2))
    
    plt.close('all')



def test_plot_lines_from_poly():
    # subsample is False if 
    ax = r2.plot()
    lines = ax.lines

    assert len(lines) == 2
    assert np.allclose(ax.lines[0].get_xydata(), r2.coords[0])
    
    plt.close('all')


def test_plot_line_prop():
    ax = r1.plot(subsample=False, line_kws=dict(lw=2, color='g'))

    lines = ax.lines

    assert lines[0].get_lw() == 2
    assert lines[0].get_color() == 'g'
    
    plt.close('all')

def test_plot_label():
    ax = r1.plot(subsample=False)
    texts = ax.texts

    # default text is the number
    assert len(texts) == 2
    assert texts[0].get_text() == '0'
    assert texts[1].get_text() == '1'

    # they are at the centroid
    assert np.allclose(texts[0].get_position(), (0.5, 0.5))
    assert np.allclose(texts[1].get_position(), (0.5, 1.5))

    plt.close('all')

    # no label
    ax = r1.plot(subsample=False, add_label=False)
    texts = ax.texts
    assert len(texts) == 0

    plt.close('all')

    # label: abbrev
    ax = r1.plot(subsample=False, label='abbrev')
    texts = ax.texts

    assert len(texts) == 2
    assert texts[0].get_text() == 'uSq1'
    assert texts[1].get_text() == 'uSq2'

    plt.close('all')

    # label: name
    ax = r1.plot(subsample=False, label='name')
    texts = ax.texts

    assert len(texts) == 2
    assert texts[0].get_text() == 'Unit Square1'
    assert texts[1].get_text() == 'Unit Square2'
    
    plt.close('all')


def test_plot_text_prop():

    ax = r1.plot(subsample=False, text_kws=dict(fontsize=15))
    texts = ax.texts
    
    assert texts[0].get_fontsize() == 15
    assert texts[1].get_fontsize() == 15
    
    assert texts[0].get_va() == 'center'

    bbox = texts[0].get_bbox_patch()
    assert bbox.get_edgecolor() == (0.85, 0.85, 0.85, 1.0)


    plt.close('all')
