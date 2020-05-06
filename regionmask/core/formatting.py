"""String formatting routines for __repr__."""

import geopandas as gp
import six
from pandas.io.formats import console


def pretty_print(x, numchars, right=True):
    """Given an object `x`, call `str(x)` and format the returned string so
    that it is numchars long, padding with trailing spaces or truncating with
    ellipses as necessary
    """

    # copied from xarray

    s = maybe_truncate(x, numchars)
    if right:
        return s + " " * max(numchars - len(s), 0)

    return " " * max(numchars - len(s), 0) + s


def maybe_truncate(obj, maxlen=500):

    # copied from xarray

    s = six.text_type(obj)
    if len(s) > maxlen:
        s = s[: (maxlen - 3)] + "..."
    return s


def _display_metadata(name, source, max_width=80):
    pad = 10

    name = pretty_print("Name:", pad) + maybe_truncate(name, max_width - pad)
    summary = [name]

    if source is not None:
        source = pretty_print("Source:", pad) + maybe_truncate(source, max_width - pad)
        summary.append(source)

    return summary


def _display_regions_gp(self, max_rows, max_width, max_colwidth):  # pragma: no cover
    summary = ["Regions:"]

    data = dict(
        numbers=self.numbers,
        abbrevs=self.abbrevs,
        names=self.names,
        # __repr__ of polygons can be slow
        # geometry=self.polygons,
    )

    df = gp.GeoDataFrame.from_dict(data)

    summary.append(
        df.to_string(
            columns=["numbers", "abbrevs", "names"],
            max_rows=max_rows,
            max_cols=0,
            line_width=max_width,
            # max_colwidth=max_colwidth,
            show_dimensions=False,
            index=False,
            header=False,
        )
    )

    return summary


def _display(self, max_rows=10, max_width=None, max_colwidth=50):

    summary = ["<regionmask.{}>".format(type(self).__name__)]

    if max_rows is None:
        max_rows = len(self)

    if max_width is None:
        max_width, _ = console.get_console_size()

    summary += _display_metadata(self.name, self.source, max_width=max_width)
    summary.append("")
    summary += _display_regions_gp(self, max_rows, max_width, max_colwidth)

    summary.append("")
    summary.append("[{:d} regions]".format(len(self)))

    return "\n".join(summary)
