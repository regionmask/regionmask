import os
import zipfile

import requests

_default_cache_dir = os.sep.join(('~', '.regionmask_data'))
longdir = os.path.expanduser(_default_cache_dir)



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
    url = download_regions_config[dataset_key]['download']['url']
    if download_regions_config[dataset_key]['download']['url'] is None:
        print(download_regions_config[dataset_key]['download']['manually'])
    else:
        assert is_downloadable(url)

    file_name = url.split('/')[-1]

    destination = f'{longdir}/{file_name}'
    download_to(url, destination)

    file_extension = file_name.split('.')[-1]

    if file_extension in ['zip']:
        unzip(destination)
        os.remove(destination)
    return
