
from __future__ import (absolute_import, division, print_function)

import glob
import os
import tempfile
import six
import zipfile


if six.PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

_writable_dir = os.path.join(os.path.expanduser('~'), '.local', 'share')
_data_dir = os.path.join(_writable_dir, 'regionmask')

def _maybe_download(url, data_dir=_data_dir, category='natural_earth'):
    """download from url and extract zip if not already done"""

    # get the last part of the url
    basename = os.path.basename(url)
    # without the file ending
    name = os.path.splitext(basename)[0]

    target_dir = os.path.join(data_dir, category, name)

    # two basic checks if the data is already available
    is_dir = os.path.isdir(target_dir)
    has_file = len(glob.glob(os.path.join(target_dir, '*')))
    
    if not is_dir or not has_file:
        _download(url, target_dir, basename)

    return target_dir



def _download(url, target_dir, basename):
    """download from url and extract zip """

    # get name of temporary folder
    tempdir = tempfile.gettempdir()
    temp_path = os.path.join(tempdir, basename)

    response = urlopen(url)
    print('Downloading: ', basename)
    with open(temp_path, 'wb') as fh:
        fh.write(response.read())
    
    print('Extracting:', basename, 'to:', target_dir)
    with zipfile.ZipFile(temp_path, "r") as z:
        z.extractall(target_dir)

    return target_dir
