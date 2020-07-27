# -*- coding: utf-8 -*-

from regionmask.core import formatting
from regionmask.defined_regions import srex


def test_pretty_print():
    assert formatting.pretty_print("abcdefghij", 8) == "abcde..."
    assert formatting.pretty_print(u"ß", 1) == u"ß"
    assert formatting.pretty_print("x", 3) == "x  "
    assert formatting.pretty_print("x", 3, False) == "  x"


def test_maybe_truncate():
    assert formatting.maybe_truncate(u"ß", 10) == u"ß"
    assert formatting.maybe_truncate("abcdefghij", 8) == "abcde..."


def test_repr_srex():

    result = srex.__repr__()

    expected = """<regionmask.Regions>
Name:     SREX
Source:   Seneviratne et al., 2012 (https://www.ipcc.ch/site/assets/uploads/2...

Regions:
  1  ALA        Alaska/N.W. Canada
  2  CGI      Canada/Greenl./Icel.
  3  WNA          W. North America
  4  CNA          C. North America
  5  ENA          E. North America
..   ...                       ...
 22  EAS                   E. Asia
 23  SAS                   S. Asia
 24  SEA                 S.E. Asia
 25  NAU              N. Australia
 26  SAU  S. Australia/New Zealand

[26 regions]"""

    assert result == expected


def test_display_metadata():

    expected = ["Name:     name"]
    result = formatting._display_metadata("name", None)
    assert result == expected

    expected = ["Name:     name", "Source:   source"]
    result = formatting._display_metadata("name", "source")
    assert result == expected

    expected = ["Name:     na..."]
    result = formatting._display_metadata("name of regions", source=None, max_width=15)
    assert result == expected
