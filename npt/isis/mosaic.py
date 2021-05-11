# from . import isissh
from . import sh

def mosaic(filename_mapcubs_list='mapcubs.list', filename_mosaic='mosaic.cub'):
    automos = sh.wrap('automos')
    res = automos(FROMLIST=filename_mapcubs_list, MOSAIC=filename_mosaic)
    sh.log(res)
    return res
