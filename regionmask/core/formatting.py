"""String formatting routines for __repr__."""

from pandas.io.formats import console


def maybe_truncate(obj, maxlen=500):

    # copied from xarray

    s = str(obj)
    if len(s) > maxlen:
        s = s[: max(maxlen - 3, 0)] + "..."
    return s


def _display_metadata(source, overlap, max_width=80):

    summary = []

    if source is not None:
        source = maybe_truncate(f"Source:   {source}", max_width)
        summary.append(source)

    overlap = f"overlap:  {overlap}"
    summary.append(overlap)

    return summary


def _display_regions_gp(self, max_rows, max_width):
    summary = ["Regions:"]

    # __repr__ of polygons can be slow -> use pd.DataFrame
    df = self.to_dataframe().reset_index()

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


def _display(self, max_rows=10, max_width=None):

    if max_width is None:
        max_width, _ = console.get_console_size()

    title = f"<regionmask.{type(self).__name__} '{self.name}'>"
    summary = [maybe_truncate(title, max_width)]

    if max_rows is None:
        max_rows = len(self)

    summary += _display_metadata(self.source, self.overlap, max_width=max_width)
    summary.append("")
    summary += _display_regions_gp(self, max_rows, max_width)

    summary.append("")
    summary.append(f"[{len(self):d} regions]")

    return "\n".join(summary)
