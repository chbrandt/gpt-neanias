import os

# 'sh' is a global (singleton) object.
from ._sh import sh


def define_projection(list_files, projection='sinusoidal', precision=5, tmpdir=None):
    #TODO: add "filename" argument to write map-definition

    # That may look strange...and maybe it is
    # I'm going to "echo" the list of filenames for if the is using docker
    # and some path needs to be mapped (host -> container), then going through
    # 'sh' will do it, since any existing mapping will happen to ("echo") also.
    echo = sh.wrap('echo')
    res = echo(*list_files)
    list_files = res.split()

    tmpdir = tmpdir or ''
    file_list = os.path.join(tmpdir, 'files_to_project.list')
    with open(file_list, 'w') as fp:
        fp.write('\n'.join(list_files))
        fp.write('\n')
    file_proj = os.path.join(tmpdir, projection+'.map')

    mosrange = sh.wrap('mosrange')
    res = mosrange(FROMLIST=file_list, TO=file_proj,
                   PROJECTION=projection, PRECISION=precision)
    sh.log(res)
    return file_proj


def map_project(filename_in, filename_out, filename_proj):
    cam2map = sh.wrap('cam2map')
    res = cam2map(FROM=filename_in, TO=filename_out, MAP=filename_proj, PIXRES='map')
    sh.log(res)
    return res
