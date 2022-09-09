# adapted from xarray under the terms of its license - see licences/XARRAY_LICENSE


OPTIONS = {
    "display_max_rows": 10,
}


def _optional_positive_integer(name: str, value: int) -> bool:

    if not (value is None or isinstance(value, int) and value > 0):
        raise ValueError(f"'{name}' must be a positive integer or None, got '{value}'")


_VALIDATORS = {
    "display_max_rows": _optional_positive_integer,
}


class set_options:
    """
    Set options for regionmask in a controlled context.

    Parameters
    ----------
    display_max_rows : int, default: 10
        Maximum display rows.

    Examples
    --------
    It is possible to use ``set_options`` either as a context manager:

    >>> srex = regionmask.defined_regions.srex
    >>> with regionmask.set_options(display_max_rows=1):
    ...     print(srex)
    <xarray.Dataset>
    Dimensions:  (x: 1000)
    Coordinates:
      * x        (x) int64 0 1 2 ... 998 999
    Data variables:
        *empty*
    Or to set global options:
    >>> xr.set_options(display_width=80)  # doctest: +ELLIPSIS
    <xarray.core.options.set_options object at 0x...>
    """

    def __init__(self, **kwargs):
        self.old = {}
        for key, value in kwargs.items():
            if key not in OPTIONS:
                raise ValueError(
                    f"{key!r} is not in the set of valid options {set(OPTIONS)!r}"
                )

            _VALIDATORS[key](key, value)

            self.old[key] = OPTIONS[key]
        self._apply_update(kwargs)

    def _apply_update(self, options_dict):
        OPTIONS.update(options_dict)

    def __enter__(self):
        return

    def __exit__(self, type, value, traceback):
        self._apply_update(self.old)


def get_options():
    """
    Get options for xarray.
    See Also
    ----------
    set_options
    """
    return OPTIONS
