import logging
import os
from glob import glob

from npt import log
from npt import isis
from npt.pipelines import processing


def main(input_path):
    batch_dir = os.path.basename(input_path.rstrip('/'))

    output_path = os.path.join('reduced', batch_dir)
    if os.path.isdir(output_path):
        log.warning(f'Directory {output_path} already exist. Skipping')
        return False
    os.makedirs(output_path, exist_ok=True)

    tmpdir = os.path.join('temp', batch_dir)
    os.makedirs(tmpdir, exist_ok=True)

    input_files = glob(os.path.join(input_path, '*.IMG'))
    for input_file in input_files:
        log.info(f'Processing file {input_file}')
        try:
            processing.run_file(input_file, output_path, tmpdir=tmpdir)
        except Exception as err:
            log.error(err)

    return True


if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="Eg, 'upstream/mrox_0010'")
    parser.add_argument('docker', help="ISIS3 docker container")

    args = parser.parse_args()

    fh = logging.FileHandler(args.docker + '.log')
    log.addHandler(fh)

    isis.set_docker(args.docker)
    try:
        main(args.input)
    except Exception as err:
        log.error(err)
        sys.exit(1)
        
    sys.exit(0)
