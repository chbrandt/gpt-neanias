"""
Query services and APIs:
- ODE
"""
from .ode import available_product_types

# def bbox(bounding_box, dataset_id, how):
#     ode_result = ode.bbox(bounding_box, dataset_id, how)
#     print("ODE RESULTS:", ode_result)
#     products = ode.parse_products(ode_result, ode.DESCRIPTORS[dataset_id])
#     print("ODE PRODUCTS:", products)
#     geojson = ode.to_geojson(products)
#     return geojson



def product_type(ptid, bbox, how='intersect', pattern=None):#, selectors=None):
    """
    Return GeoJSON with products found in/at bounding-box

    Input:
    - ptid : string
        Identify the product-type to search inside/over 'bbox'
        See ~ODE.product_types for a list of supported product-types
    - bbox : ~Bbox
        Bounding-box in degrees to to search for intersect/containing images
    - how : string
        Search for products intersecting or contained in the bounding-box
    - pattern : string
        A regular-expression to filter product-IDs

    Output:
        GeoJSON containing all products found
    """
    from . import ode
    # assert ptid in ode.available_product_types(), f"Product type not supported."
    search = ode.Search(ptid)
    results = search.bbox(bbox, how=how)
    if pattern:
        results = results.filter(pattern=pattern)
    return results
