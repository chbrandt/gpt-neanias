"""
Download files (from HTTPS) tools
"""
import os
import sys
import shutil
import requests
from . import log


def download_file(url, filename=None, progress=False, make_dirs=True):
    """
    Download file under 'url'.

    Args:
        url: str
            URL (file) to download
        filename: str
            Relative or absolute path for content from 'url'.
            If None, URL's file name is used.
        progress: bool
            If True, show a (tqdm) progress bar.
        make_dirs: bool
            If True, create necessary directories to write output (filename).
            If False,

    Return:
        Downloaded file name, or None in case of failure
    """
    progress_on = progress

    if not filename:
        local_filename = os.path.join('.', url.split('/')[-1])
    else:
        local_filename = filename

    if is_download_complete(url, local_filename):
        log.debug("File '{}' from '{}' already downloaded".format(local_filename, url))
        return local_filename

    _path = os.path.dirname(local_filename)
    if not os.path.isdir(_path):
        if make_dirs:
            os.makedirs(_path, exist_ok=True)
        else:
            print("Path '{}' does not exist.".format(_path))
            return None

    print('--> Downloading file {} ..'.format(local_filename))
    ok = False
    if progress_on:
        ok = _progressbar(url, local_filename)
    else:
        ok = _quiet(url, local_filename)
    if not ok:
        log.info("File '{}' could not be downloaded.".format(local_filename))
        return None

    print("File '{}' downloaded.".format(local_filename))
    return local_filename


def download_files(urls, descriptors=None, filenames=None, path=None, progress=False):
    """
    Download list of files given 'urls'. Return a {"descriptors":"filenames"}.

    TODO: return list of filenames (and 'None's)

    Args:
        urls: List(str)
        descriptors: Dict(obj:str)
            unique ids, if empty an integer integer set is created
        filenames: List(str)
            Filenames for each url, len(filenames)==len(urls)
            Filenames will be written under 'path' (if in relative paths)
        path: str
            base path for 'filenames' (for filenames in relative paths)
        progress: bool
            If True, show a (tqdm) progress bar

    Return:
        This dictionary or {"descriptors":"filenames"}
    """
    progress_on = progress
    assert isinstance(urls, (list, tuple))

    if not filenames:
        filenames = [os.path.join(path, url.split('/')[-1]) for url in urls]
    assert len(filenames) == len(urls), "List of 'filenames' must match length of 'urls'"

    if not descriptors:
        descriptors = list(range(len(urls)))
    assert len(set(descriptors)) == len(descriptors), "List of 'descriptors' should be unique values"
    assert len(descriptors) == len(urls), "List of 'descriptors' must match length of 'urls'"

    files_downloaded = {}
    for url, descriptor, filename in zip(urls, descriptors, filenames):
        try:
            _fn = download_file(url, filename, progress_on)
            files_downloaded[descriptor] = _fn
        except Exception as err:
            log.debug(err)

    return files_downloaded


def is_download_complete(url, filename):
    """
    Return True if the sizes of remote/url file and (local) filename are the same
    """
    if not os.path.isfile(filename):
        log.debug("File '{}' does not exist.".format(filename))
        return False

    log.debug("File '{}' exist.".format(filename))
    try:
        r = requests.get(url, stream=True)
        remote_size = int(r.headers['Content-Length'])
        local_size = int(os.path.getsize(filename))
    except Exception as err:
        log.error(err)
        return False
    log.debug("Remote file size: " + str(remote_size))
    log.debug("Local file size: " + str(local_size))
    return local_size == remote_size


# Couple of aliases to make the calls smaller
#
file = download_file
files_list = download_files
is_downloaded = is_download_complete
# ===========================================


def _quiet(url, filename):
    """
    Download file (silently)

    Usage:
        _quiet('http://web4host.net/5MB.zip', 'local_filename.zip')
    """
    try:
        r = requests.get(url)
        with open(filename,'wb') as f:
            f.write(r.content)
    except Exception as err:
        log.error(err)
        return False
    return True

in_silence = _quiet


def _progressbar(url, filename, verbose=False):
    """
    Download file with progressbar

    Usage:
        _progressbar('http://web4host.net/5MB.zip', 'local_filename.zip')
    """
    import tqdm
    try:
        r = requests.get(url, stream=True)
        file_size = int(r.headers['Content-Length'])
        chunk = 1
        chunk_size=1024
        num_bars = int(file_size / chunk_size)
        if verbose:
            log.info(dict(file_size=file_size))
            log.info(dict(num_bars=num_bars))

        with open(filename, 'wb') as fp:
            for chunk in tqdm.tqdm(
                                        r.iter_content(chunk_size=chunk_size)
                                        , total= num_bars
                                        , unit = 'KB'
                                        , desc = filename
                                        , leave = True # progressbar stays
                                    ):
                fp.write(chunk)
    except Exception as err:
        log.error(err)
        return False

    return True

with_progressbar = _progressbar
