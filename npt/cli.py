"""
Define commands and sub-commands line interface
"""
import click
from click import argument,option

from npt import log

# from npt.search import bbox as search_bbox
from npt.pipelines import Search
from npt.utils.formatters import json_2_geojson
from npt.utils.bbox import string_2_dict as bbox_string_2_dict

from npt.pipelines import Download
from npt.utils import geojson

from npt.pipelines import Processing



# === MAIN
@click.group()
@option('--debug', is_flag=True, default=False, help="Output DEBUG-level messages")
def main(debug):
    """
    Interface to npt pipelines
    """
    if debug:
        log.setLevel('DEBUG')
# ===



@main.command()
@argument('dataset')
@option('--bbox', default=None, help='Bounding-box where to search products')
@option('--geojson_out', default='', help="GeoJSON filename with query results")
@option('--contain/--intersect', default=False, help="Bounding-box intersects or contains products' footprint")
def search(bbox=None, dataset=None, geojson_out=None, contain=False):
    """
    Query 'provider'/'dataset' for data products in/on 'bbox'

    \b
    Attributes:
    - provider: 'ODE'
        Query ODE for intersecting footprints to bbox.
    - dataset: <string>
        Options are: ['mars/mro/ctx/edr', 'mars/mro/hirise/rdrv11'].
    - bbox: <string>
        Format: '[min,max,west,east]' (global positive east [0:360])
        Eg,
            "[-0.5,0.5,359.5,0.5]"

    """
    return _search(bbox, dataset, geojson_out, contain)

def _search(bbox=None, dataset=None, geojson_out=None, contain=False):
    log.fair(locals())

    if None in (bbox, dataset):
        return False

    bbox = bbox.replace('[','').replace(']','')
    bounding_box = bbox_string_2_dict(bbox)
    log.debug("Bounding-box: {!s}".format(bounding_box))

    if output:
        products = Search.run(bounding_box=bounding_box,
                           geojson_filename=output,
                           dataset_id=dataset,
                           contains=contains)
    else:
        import json
        products = Search.run(bounding_box=bounding_box,
                           dataset_id=dataset,
                           contains=contains)
        click.echo(json.dumps(products, indent=2))


@main.command()
@argument('geojson_file')
@argument('basepath')
@option('--output', metavar='<.geojson>', default='', help="GeoJSON filename with query results")
@option('--progress/--silent', default=True, help="Print download progress")
@option('--parallel/--serial', default=False, help="Download in parallel")
def download(geojson_file, basepath, output, progress, parallel):
    """
    Download features' image_url/label_url data products
    """
    log.args(locals())

    features = geojson.read(geojson_file)
    log.info("{:d} features read".format(len(features)))

    products = []
    for feature in features:
        log.info("Feature {:d}/{:d}".format(i+1, len(features)))
        mod_feature = Download.run(feature, base_path=basepath, progressbar=progress)
        products.append(mod_feature)

    if output:
        json_2_geojson(products, filename=output)
    else:
        import json
        click.echo(json.dumps(products, indent=2))


@main.command()
@argument('geojson_file')
@argument('basepath')
@option('--output', default=None, help="GeoJSON filename with query results")
@option('--parallel/--serial', default=False, help="Process in parallel")
@option('--docker-isis', default=None, help="ISIS3 Docker container to use")
@option('--tmpdir', default=None, help="Temp dir to use during processing")
def process(geojson_file, basepath, parallel, docker_isis, tmpdir, output, dataset):
    """
    Reduce CTX data
    """
    log.args(locals())

    features = geojson.read(geojson_file)
    log.info("{:d} features read".format(len(features)))

    if docker_isis:
        log.debug(f"Docker: {docker_isis}")
        #FIXME: this is terrible...an import in the middle of the code
        from npt import isis
        isis.set_docker(docker_isis)

    products = []
    for i,feature in enumerate(features):
        log.info("Feature {:d}/{:d}".format(i+1, len(features)))
        mod_feature = Processing.reduce(feature,
                                        dataset,
                                        output_path=basepath,
                                        tmpdir=tmpdir)
        products.append(mod_feature)

    if output:
        json_2_geojson(products, filename=output)
    else:
        import json
        click.echo(json.dumps(products, indent=2))


@main.command()
@argument('filespath')
@argument('basepath')
def mosaic(input_geojson, basepath, output, output_field='mosaic_path',
            sources_field='mosaic_sources', tmpdir='tmp/'):
    """
    Make mosaic from files in 'input_geojson' file. Write GeoJSON with mosaic feature.
    """
    log.args(locals())

    features = geojson.read(input_geojson)
    log.info("{:d} features read".format(len(features)))

    filenames = [ f['properties'][input_field] for f in features ]
    mosaic_path = Processing.mosaic(filenames,
                                    output_path=basepath,
                                    tmpdir=tmpdir)

    # Define the new feature (mosaic)
    filenames = ','.join(filenames)
    feature = {
        'properties': {
            output_field: mosaic_path,
            sources_field: filenames,
        },
        'geometry': None
    }
    products = [feature]

    if output:
        json_2_geojson(products, filename=output)
    else:
        import json
        click.echo(json.dumps(products, indent=2))
    raise NotImplementedError



if __name__ == '__main__':
    main()
