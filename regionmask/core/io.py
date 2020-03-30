import os
import zipfile
import yaml

import requests

_default_cache_dir = os.sep.join(('~', '.regionmask_data'))
longdir_cache = os.path.expanduser(_default_cache_dir)

fn_download_yaml = "regionmask/defined_regions/download_regions.yaml"
with open(fn_download_yaml, 'r') as f:
    metadata = yaml.safe_load(f)
    keywords_dict = {}
    for k, v in metadata.items():
        keywords_dict[k] = k
        if v['keywords'] is not None:
            for keyword in v['keywords']:
                keywords_dict.update({keyword: k})

with open(fn_download_yaml) as f:
    download_regions_config = yaml.safe_load(f)
f.close()


def is_downloadable(url):
    """
    Does the url contain a downloadable resource?

    Parameters
    ----------
    url : str
        String of url.

    Returns
    -------
    boolean

    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def download_to(url, destination):
    """
    Download url to destination.

    Parameters
    ----------
    url : str
        String of url.
    destination: str
        String of path

    """
    r = requests.get(url, allow_redirects=True)
    open(destination, 'wb').write(r.content)
    return


def unzip(filename_str):
    """
    Unzip zip file.

    Parameters
    ----------
    filename_str : str
        Location of zip file.

    """
    zip_ref = zipfile.ZipFile(filename_str, 'r')
    zip_ref.extractall(filename_str.strip('.zip'))
    zip_ref.close()
    return


def download_dataset(dataset_key):
    """
    Download a dataset given by dataset_key in download_regions.yaml.

    Parameters
    ----------
    dataset_key : str
        String of dataset_key. Must be in download_regions.yaml as keyword.

    """
    if not os.path.exists(longdir_cache):
        os.makedirs(longdir_cache)
    url = download_regions_config[dataset_key]['download']['url']
    if url is None:
        raise ValueError(download_regions_config[dataset_key]['download']['manually'])
    else:
        assert is_downloadable(url)

    file_name = url.split('/')[-1]

    destination = f'{longdir_cache}/{file_name}'
    download_to(url, destination)

    file_extension = file_name.split('.')[-1]

    if file_extension in ['zip']:
        unzip(destination)
        os.remove(destination)
    return
