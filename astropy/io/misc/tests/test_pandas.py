# Licensed under a 3-clause BSD style license - see LICENSE.rst

from io import StringIO

import pytest
import numpy as np

from astropy.io import ascii
from astropy.table import Table, QTable
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io.misc.pandas.connect import PANDAS_FMTS

pandas = pytest.importorskip("pandas")

WRITE_FMTS = [fmt for fmt in PANDAS_FMTS if 'write' in PANDAS_FMTS[fmt]]


@pytest.mark.parametrize('fmt', WRITE_FMTS)
def test_read_write_format(fmt):
    """
    Test round-trip through pandas write/read for supported formats.

    :param fmt: format name, e.g. csv, html, json
    :return:
    """
    pandas_fmt = 'pandas.' + fmt
    t = Table([[1, 2, 3], [1.0, 2.5, 5.0], ['a', 'b', 'c']])
    buf = StringIO()
    t.write(buf, format=pandas_fmt)

    buf.seek(0)
    t2 = Table.read(buf, format=pandas_fmt)

    assert t.colnames == t2.colnames
    assert np.all(t == t2)


def test_read_fixed_width_format():
    """Test reading with pandas read_fwf()

    """
    tbl = """\
    a   b   c
    1  2.0  a
    2  3.0  b"""
    buf = StringIO()
    buf.write(tbl)

    t = Table.read(tbl, format='ascii', guess=False)

    buf.seek(0)
    t2 = Table.read(buf, format='pandas.fwf')

    assert t.colnames == t2.colnames
    assert np.all(t == t2)


def test_write_with_mixins():
    """Writing a table with mixins just drops them via to_pandas()

    This also tests passing a kwarg to pandas read and write.
    """
    sc = SkyCoord([1, 2], [3, 4], unit='deg')
    q = [5, 6] * u.m
    qt = QTable([[1, 2], q, sc], names=['i', 'q', 'sc'])

    buf = StringIO()
    qt.write(buf, format='pandas.csv', sep=' ')
    exp = ['i q sc.ra sc.dec',
           '1 5.0 1.0 3.0',
           '2 6.0 2.0 4.0']
    assert buf.getvalue().splitlines() == exp

    # Read it back
    buf.seek(0)
    qt2 = Table.read(buf, format='pandas.csv', sep=' ')
    exp_t = ascii.read(exp)
    assert qt2.colnames == exp_t.colnames
    assert np.all(qt2 == exp_t)
