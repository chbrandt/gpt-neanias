"""
Mosaic related Functions

The basic idea of this mosaic'ing module is to offer a function to handle the
list of images to mosaic from a geojson file (which is the media used by MEEO).
"""

def run(geojson_filename):
    """
    Create mosaic from given images. Return geojson for resulting mosaic.

    Input:
        * geojson_filename : string

    Output:
        GeoJSON (object)
    """
    from npt.utils import geojson

    gjs = geojson.read(geojson_filename)

    features = geojson.copy_features(gjs)
    new_features = _run_features(features)
    assert len(new_features) == 1, """
        Resulting number features from a mosaic is expected to be '1',
        instead got {len(new_features)}
        """

    geojson_out = None
    return geojson_out

from_geojson = run


def _run_features(features: list) -> list:
    """
    Input:
        * features : list
            List of geojson features
    """
    # because mosaic processing is processed in batch (all source "together"),
    # and also because the input geojson/features-list can contain image/data
    # from different datasets (i.e, product_types), we first want to go
    # through each and all of them and organize after the datasets, in lists also.
    def _groupby_dataset(features: list) -> dict:
        """
        Return dictionary if list of features after each dataset/product_type
        """
        data_sets = {}
        for feature in features:
            properties = feature['properties']
            target = properties['targetName']
            mission = properties['mission']
            instrument = properties['instrumentId']
            product_type = properties['observationMode']
            datasetId = f"{target}/{mission}/{instrument}/{product_type}".lower()
            data_sets[datasetId] = data_sets.get(datasetId, []) + [feature]
        return data_sets

    data_sets = _groupby_dataset(features)
    log.debug(f"Datasets/product-types involved in this mosaic: {data_sets.keys()}")

    for d_id, features in data_sets.items():
        if d_id == 'mars/mro/ctx/edr':
            mosaic_ctx(features)
    # properties = _run_props(properties, output_path, projection, tmpdir, datasetId)
    # feature['properties'] = properties
    # pass
    assert None


def mosaic_ctx(features: list, engine='isis'):
    """
    Input:
        - features : list of geo-features
        Each feature contain in properties 'image_path' (isis) or 'tiff_path' (gdal)
        - engine : string
        Options are ['isis','gdal']
    """
    if engine == 'isis':
        from npt.isis.mosaic import mosaic
        path_field = 'image_path'
        ext = 'cub'
    else:
        assert engine == 'gdal'
        from npt.gdal.mosaic import mosaic
        path_field = 'tiff_path'
        ext = 'tif'

    # _pf = 'properties'
    # input_filenames = [ f[_p][path_field] for f in features ]
    # output_filename = '.'.join('mosaic',ext)

    import geopandas
    gdf = geopandas.GeoDataFrame.from_features(features)
    input_filenames = list(gdf[path_field])

    output_filename = mosaic(input_filenames, output_filename)
    if not output_filename:
        return None
