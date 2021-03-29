"""
Query ODE API for different (PDS) datasets (http://oderest.rsl.wustl.edu/)
"""
import requests

from npt import log


_URL = 'https://oderest.rsl.wustl.edu/live2'

DESCRIPTORS = {
    'mars/mro/ctx/edr': {
        'product_image': ('Description','PRODUCT DATA FILE WITH LABEL'),
        'browse_image': ('Description','BROWSE IMAGE'),
        'browse_thumbnail': ('Description','THUMBNAIL IMAGE')
    },
    'mars/mro/hirise/rdrv11': {
        'product_image': ('Description', 'PRODUCT DATA FILE'),
        'product_label': ('Description', 'PRODUCT LABEL FILE'),
        'browse_image': ('Description', 'BROWSE'),
        'browse_thumbnail': ('Description', 'THUMBNAIL')
    },
    'mars/mex/hrsc/rdrv3': {
        'product_image': ('Description', 'PRODUCT DATA FILE WITH LABEL'),
        'browse_image': ('Description', 'BROWSE IMAGE'),
        'product_shapefiles': ('Description', 'PRODUCT FOOTPRINT SHAPEFILES (TAR.GZ) *')
    }
}

_schema = {
    'bbox': {'minlat': float, 'maxlat': float, 'westlon': float, 'eastlon': float}
}

def bounding_box(bbox, dataset, how='intersect'):
    """
    Return GeoJSON with products intersecting 'bounding_box'

    Args:
        bbox: dictionary
            {'minlat': float, 'maxlat': float, 'westlon': float, 'eastlon': float}
            Longitudes are in the range [0:360] (180 center).
        dataset: string
            Datasets identifiers.
            Options are 'mars/mro/ctx/edr', 'mars/mro/hirise/rdrv11'.
        how: string
            Options are 'intersect', 'contain'
    Return:
        GeoJSON format dictionary with data products as features

    Example:
    > bbox({'minlat': -0.5, 'maxlat': 0.5, 'westlon': 359.5, 'eastlon': 0.5},
           dataset='mro/hirise/rdrv11')
    """
    target,host,instr,ptype = dataset.split('/')

    assert all(k in _schema['bbox'] for k in bbox), "Expected 'bounding_box' like: _schema['bbox']"

    res = _query_ODE(_set_payload(bbox, target, host, instr, ptype, how=how))
    log.debug("Request result: {!r}".format(res))

    status = res['ODEResults']['Status']
    if status.lower() != 'success':
        log.error('Request failed: {!s}'.format(res))
        return None
    return res

bbox = bounding_box


def parse_products(odejson, descriptor):
    try:
        products = odejson['ODEResults']['Products']['Product']
    except:
        return None

    products = products if isinstance(products, (list,tuple)) else [products]

    products_output = []
    for i,product in enumerate(products):
        log.debug(i,product)
        _meta = _readout_product_meta(product)
        _files = _readout_product_files(product)
        _fprint = _readout_product_footprint(product)
        _pfile = _find_product_file(product_files=_files,
                                    product_type='product_image',
                                    descriptor=descriptor)
        _pfile = _pfile['URL']
        try:
            _lfile = _find_product_file(product_files=_files,
                                        product_type='product_label',
                                        descriptor=descriptor)
            _lfile = _lfile['URL']
        except KeyError as err:
            _lfile = _pfile

        _dout = _meta
        _dout['geometry'] = _fprint
        _dout['image_url'] = _pfile
        _dout['label_url'] = _lfile
        products_output.append(_dout)

    print("{} products found".format(len(products_output)))
    return products_output


def _query_ODE(payload):
    #payload.update({'pretty':True})
    return requests.get(_URL, params=payload).json()


def _set_payload(bbox, target=None, host=None, instr=None, ptype=None, how='intersect'):
    payload = dict(
        query='product',
        results='fmpc',
        output='JSON',
        loc='f',
        minlat=bbox['minlat'],
        maxlat=bbox['maxlat'],
        westlon=bbox['westlon'],
        eastlon=bbox['eastlon']
    )

    if target:
        payload.update({'target':target})
    if host:
        payload.update({'ihid':host})
    if instr:
        payload.update({'iid':instr})
        if ptype:
            payload.update({'pt':ptype})

    if 'contain' in how:
        payload.update({'loc':'o'})

    return payload


def _readout_product_files(product_json):
    product_files = product_json['Product_files']['Product_file']
    return product_files


def _readout_product_footprint(product_json):
    # 'Footprint_geometry' and 'Footprint_C0_geometry' may contain 'GEOMETRYCOLLECTION'
    # when the footprint cross the meridian in "c180" or "c0" frames
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_geometry']
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_C0_geometry']
    product_geom = product_json['Footprint_GL_geometry']
    return product_geom


def _readout_product_meta(product_json):
    product = {}
    # <pdsid>ESP_011712_1820_COLOR</pdsid>
    product['id'] = product_json['pdsid']
    # <ihid>MRO</ihid>
    product['mission'] = product_json['ihid']
    # <iid>HIRISE</iid>
    product['inst'] = product_json['iid']
    # <pt>RDRV11</pt>
    product['type'] = product_json['pt']
    return product


def _find_product_file(product_files, product_type, descriptor):
    _key,_val = descriptor[product_type]
    pfl = list(filter(lambda pf:pf[_key]==_val, product_files))
    _multiple_matches = "I was expecting only one Product matching ptype '{}' bu got '{}'."
    assert len(pfl) == 1, _multiple_matches.format(product_type, len(pfl))
    return pfl[0]
