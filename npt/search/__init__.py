"""
Query services and APIs:
- ODE
"""
from . import ode

def bbox(bounding_box, dataset_id, how):
    ode_result = ode.bbox(bounding_box, dataset_id, how)
    products = ode.parse_products(ode_result, search.ode.DESCRIPTORS[dataset_id])
    geojson = ode.to_json(products)
    return geojson
