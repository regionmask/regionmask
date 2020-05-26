import io
import os

import yaml
from cartopy.io import Downloader

_default_cache_dir = os.sep.join(("~", ".regionmask_data"))
longdir_cache = os.path.expanduser(_default_cache_dir)
if not os.path.exists(longdir_cache):
    os.mkdir(longdir_cache)

fn_download_yaml = "regionmask/defined_regions/downloadable_regions.yaml"
with open(fn_download_yaml, "r") as f:
    metadata = yaml.safe_load(f)
    keywords_dict = {}
    for k, v in metadata.items():
        keywords_dict[k] = k
        if v["keywords"] is not None:
            for keyword in v["keywords"]:
                keywords_dict.update({keyword: k})

with open(fn_download_yaml) as f:
    download_regions_config = yaml.safe_load(f)
f.close()


class RegionmaskDownloader(Downloader):
    """Copied from cartopy.io.shapereader. Close to NEShpDownloader."""

    def zip_file_contents(self, format_dict):
        """
        Return a generator of the filenames to be found in the downloaded
        natural earth zip file.
        """
        for ext in [".shp", ".dbf", ".shx"]:
            # this line got changed from cartopy
            yield "{shpfilename}{ext}".format(ext=ext, **format_dict)

    def acquire_resource(self, target_path, format_dict):
        """
        Download the zip file and extracts the files listed in
        :meth:`zip_file_contents` to the target path.
        """
        from zipfile import ZipFile

        target_dir = os.path.dirname(target_path)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        url = self.url(format_dict)

        shapefile_online = self._urlopen(url)

        zfh = ZipFile(io.BytesIO(shapefile_online.read()), "r")

        for member_path in self.zip_file_contents(format_dict):
            ext = os.path.splitext(member_path)[1]
            target = os.path.splitext(target_path)[0] + ext
            member = zfh.getinfo(member_path.replace(os.sep, "/"))
            with open(target, "wb") as fh:
                fh.write(zfh.open(member).read())

        shapefile_online.close()
        zfh.close()

        return target_path


def downloader(url, name, shpfilename):
    # downloads url if needed, returns .zip when downloaded first downloaded and shp when already downloaded
    d1 = RegionmaskDownloader(
        url, f"{longdir_cache}/{name}/{name}.zip", f"{longdir_cache}/{name}/{name}.shp"
    )
    config = {("level_1"): d1}
    d1 = RegionmaskDownloader.from_config(("level_1"), config_dict=config)
    format_dict = {"config": config, "name": name, "shpfilename": shpfilename}
    return d1.path(format_dict)


def download_dataset(dataset_key):
    """
    Download a dataset given by dataset_key in download_regions.yaml.
    Parameters
    ----------
    dataset_key : str
        String of dataset_key. Must be in download_regions.yaml as keyword.
    """
    if dataset_key not in keywords_dict:
        raise ValueError(
            f"{dataset_key} not found in keywords: "
            f"Please select from {keywords_dict.keys()}."
        )
    dataset_key = keywords_dict[dataset_key]

    url = download_regions_config[dataset_key]["download"]["url"]
    if url is None:
        raise ValueError(download_regions_config[dataset_key]["download"]["manually"])
    # else:
    #    assert is_downloadable(url)
    shpfilename = download_regions_config[dataset_key]["shpfilename"]
    return downloader(url, dataset_key, shpfilename)
