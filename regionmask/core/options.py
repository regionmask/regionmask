# adapted from xarray under the terms of its license - see licences/XARRAY_LICENSE


OPTIONS = {
    "display_max_rows": 10,
    "cache_dir": None,
}


def _optional_positive_integer(name: str, value) -> bool:
    if not (value is None or isinstance(value, int) and value > 0):
        raise ValueError(f"'{name}' must be a positive integer or None, got '{value}'")


def _optional_str_or_path(name: str, value) -> bool:
    from pathlib import Path

    if not (value is None or isinstance(value, (str, Path))):
        raise ValueError(f"'{name}' must be a string or pathlib.Path, got '{value}'")


_VALIDATORS = {
    "display_max_rows": _optional_positive_integer,
    "cache_dir": _optional_str_or_path,
}


class set_options:
    """
    Set options for regionmask in a controlled context.

    Parameters
    ----------
    display_max_rows : int, default: 10
        Maximum display rows.
    cache_dir : str | pathlib.Path
        Location of the cache directory. If None uses the default cache location of
        your operating system. For unix-like this would be '~/.cache/regionmask'.

    Examples
    --------
    It is possible to use ``set_options`` either as a context manager:

    >>> import regionmask
    >>> srex = regionmask.defined_regions.srex
    >>> with regionmask.set_options(display_max_rows=2):
    ...     print(srex)
    <regionmask.Regions 'SREX'>
    Source:   Seneviratne et al., 2012 (https://www.ipcc.ch/site/assets/uploads/2...
    overlap:  False
    <BLANKLINE>
    Regions:
     1 ALA       Alaska/N.W. Canada
    ..  ..                      ...
    26 SAU S. Australia/New Zealand
    <BLANKLINE>
    [26 regions]

    >>> regionmask.set_options(display_max_rows=None)  # doctest: +ELLIPSIS
    <regionmask.core.options.set_options object at 0x...>
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
    Get options for regionmask.

    See Also
    --------
    set_options
    """
    return OPTIONS
