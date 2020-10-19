import os

from . import log

from ..utils.filenames import change_extension as _change_file_extension
from ..utils.filenames import change_dirname as _change_file_dirname
from ..utils.filenames import insert_preext as _add_file_subextension



def proj_planet2earth(filein, fileout):
    from npt.utils.raster import warp
    return warp(filein, fileout)

def _run_geo_feature(geojson_feature, output_path, projection="sinusoidal", tmpdir=None):
    feature = geojson_feature.copy()
    return _run_props(feature['properties'], output_path, projection, tmpdir)

run = _run_geo_feature


def _run_props(properties, output_path, map_projection, tmpdir):
    image_filename = properties['image_path']
    return run_file(image_filename, output_path, map_projection, tmpdir)


def run_file(filename_init, output_path, map_projection="sinusoidal", tmpdir=None):
    # Create a temp dir for the processing
    import shutil
    import tempfile
    if tmpdir:
        assert os.path.isdir(tmpdir), """Given tmpdir '{}' does not exist""".format(tmpdir)
        tempfile.tempdir = tmpdir

    try:
        tmpdir = tempfile.mkdtemp(prefix='neanias_')
    except:
        log.error("Temporary directory ('{}') could not be created.".format(tmpdir))
        raise err
    else:
        log.info("Processing temporary dir: '{}'".format(tmpdir))

    try:
        f_in = shutil.copy(filename_init, tmpdir)

        # FORMAT (pds->isis)
        from npt.isis import format
        # -- Transfrom PDS (IMG) into ISIS (CUB) file
        f_cub = _change_file_extension(f_in, 'cub')
        format.pds2isis(f_in, f_cub)
        # -- Init SPICE kernel
        format.init_spice(f_cub)

        # CALIBRATION
        from npt.isis import calibration
        f_cal = _add_file_subextension(f_cub, 'cal')
        calibration.radiometry(f_cub, f_cal)

        # MAP-PROJECTION
        from npt.isis import projection
        ## Define projection
        f_map = _add_file_subextension(f_cal, 'map')
        _flist = [f_cal]
        proj_file = projection.define_projection(_flist, projection=map_projection, tmpdir=tmpdir)
        ## Project
        projection.map_project(f_cal, f_map, proj_file)

        # FORMAT to TIFF
        f_tif = _change_file_extension(f_map, 'tif')
        format.isis2tiff(f_map, f_tif)

    except Exception as err:
        log.error(err)
        raise err
    else:
        log.info("Processing finished, file '{}' created.".format(f_tif))

    try:
        log.info("Copying from temp to archive/output path")
        f_out =  _change_file_dirname(f_tif, output_path)
        shutil.move(f_tif, f_out)
    except Exception as err:
        log.error("File '{}' could not be moved to '{}'".format(f_tif, f_out))
        log.error("Temporary files, '{}' will remain. Remove them manually.".format(tmpdir))
        raise err
    finally:
        log.info("Cleaning temporary files/directory ({})".format(tmpdir))
        shutil.rmtree(tmpdir)

    return f_out