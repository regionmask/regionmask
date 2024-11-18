"""String formatting routines for __repr__."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pandas.io.formats import console  # type:ignore[attr-defined]

if TYPE_CHECKING:
    from regionmask.core.regions import Regions


def maybe_truncate(obj, maxlen: int = 500) -> str:

    # copied from xarray

    s = str(obj)
    if len(s) > maxlen:
        s = s[: max(maxlen - 3, 0)] + "..."
    return s


def _display_metadata(
    source: str | None, overlap: bool | None, max_width: int = 80
) -> list[str]:

    summary = []

    if source is not None:
        source = maybe_truncate(f"Source:   {source}", max_width)
        summary.append(source)

    overlap_ = f"overlap:  {overlap}"
    summary.append(overlap_)

    return summary


def _display_regions_gp(self: Regions, max_rows: int, max_width: int) -> list[str]:
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


def _display(self, max_rows: int = 10, max_width: int | None = None) -> str:

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
