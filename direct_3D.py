import numpy as np

from regionmask.core.utils import unpackbits


def _mask_rasterize_3D_overlap(lon, lat, polygons, **kwargs):

    # rasterize returns a flat mask, so we "bits" and MergeAlg.add to determine overlapping
    # regions. For three regions we use numbers 1, 2, 4 and then
    # 1 -> 1
    # 3 -> 1 & 2
    # 6 -> 2 & 4
    # etc

    import rasterio

    import regionmask

    numbers = 2 ** np.arange(32)
    n_polygons = len(polygons)

    out = list()

    # rasterize only supports uint32 -> rasterize in batches of 32
    for i in range(np.ceil(n_polygons / 32).astype(int)):

        sel = slice(32 * i, 32 * (i + 1))
        result = regionmask.core.mask._mask_rasterize(
            lon,
            lat,
            polygons[sel],
            numbers[: min(32, n_polygons - i * 32)],
            fill=0,
            dtype=np.uint32,
            merge_alg=rasterio.enums.MergeAlg.add,
            **kwargs
        )

        # disentangle the regions
        result = unpackbits(result, 32)
        out.append(result)

    return np.concatenate(out, axis=2)[:, :, :n_polygons]
