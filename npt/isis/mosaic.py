# from . import isissh
import os

from . import sh

def _create_files_list_file(filenames_list, tmpdir=None):
    # That may look strange...and maybe it is
    # I'm going to "echo" the list of filenames for if the is using docker
    # and some path needs to be mapped (host -> container), then going through
    # 'sh' will do it, since any existing mapping will happen to ("echo") also.
    echo = sh.wrap('echo')
    res = echo(*filenames_list)
    list_files = res.split()

    tmpdir = tmpdir or ''
    file_list = os.path.join(tmpdir, 'files.list')
    with open(file_list, 'w') as fp:
        fp.write('\n'.join(list_files))
        fp.write('\n')

    return file_list


def mosaic(filenames_list, filename_mosaic, tmpdir=None):
    filename_mapcubs_list = _create_files_list_file(filenames_list, tmpdir=tmpdir)
    automos = sh.wrap('automos')
    res = automos(FROMLIST=filename_mapcubs_list, MOSAIC=filename_mosaic)
    sh.log(res)
    return res
