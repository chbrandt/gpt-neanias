"""
Datasets dynamic import
"""
# Refs:
# - https://packaging.python.org/guides/creating-and-discovering-plugins/
# - https://stackoverflow.com/a/64124377/687896
import npt



# -----------------------------------------
# Dynamic load module in current directory:
#
# DEPRECATED
#
import sys
import pkgutil
import importlib

pkg = sys.modules[__package__]

_datasets = []
for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__, pkg.__name__+'.'):
    mod = importlib.import_module(name)
    _datasets.append(mod)

del pkg, finder, name, ispkg
del importlib, pkgutil, sys
#
# -----------------------------------------

class pds:
    @staticmethod
    def parse_image_header(filename_img):
        """
        Extract PDS LABEL (text) from PDS IMAGE
        """
        import io
        header = io.StringIO()
        with open(filename_img, 'r') as fp:
            for line in fp:
                if '\x00' in line:
                    break
                else:
                    header.write(line)

        header.seek(0)
        return header


_datasets = [
    {
        "provider": "ode",
        "target": "mars",
        "mission": "mro",
        "instrument": "ctx",
        "product_type": "edr",
        # maybe 'id' is not necessary afterall
        "id": "{target}/{mission}/{instrument}/{product_type}",
        #
        "descriptors": {
            'product_image': ('Description','PRODUCT DATA FILE WITH LABEL'),
            'product_label': (None, {
                'function':('npt.datasets.pds.parse_image_header', '{product_image}')
                }),
            'browse_image': ('Description','BROWSE IMAGE'),
            'browse_thumbnail': ('Description','THUMBNAIL IMAGE')
        }
    },
    {
        "provider": "ode",
        "target": "mars",
        "mission": "mro",
        "instrument": "hirise",
        "product_type": "rdrv11",
        # maybe 'id' is not necessary afterall
        "id": "{target}/{mission}/{instrument}/{product_type}",
        #
        "descriptors": {
            'product_image': ('Description', 'PRODUCT DATA FILE'),
            'product_label': ('Description', 'PRODUCT LABEL FILE'),
            'browse_image': ('Description', 'BROWSE'),
            'browse_thumbnail': ('Description', 'THUMBNAIL')
        }
    },
    {
        "provider": "ode",
        "target": "mars",
        "mission": "mro",
        "instrument": "hrsc",
        "product_type": "refdr3",
        # maybe 'id' is not necessary afterall
        "id": "{target}/{mission}/{instrument}/{product_type}",
        #
        "descriptors": {
            'product_image': ('Description', 'PRODUCT DATA FILE'),
            'product_label': ('Description', 'PRODUCT LABEL FILE'),
            'browse_image': ('Description', 'BROWSE'),
            'browse_thumbnail': ('Description', 'THUMBNAIL')
        }
    }
]


def _solve_datasets_references(dsets: list) -> list:
    """
    Solve datasets/dictionary internal references
    """
    def _solve_self_references(kvmaps: dict) -> dict:
        """
        Return dictionary with internal references resolved.

        Eg, for an input map like:
        '''
        {
            'a': "to be",
            'b': "or not {a}",
            'c': "{a} {b}, that is the question",
            'd': {'nested': "this is not touched, {a}, {b}, {c}"}
        }
        '''
        It should return:
        '''
        {
            'a': "to be",
            'b': "or not to be",
            'c': "to be or not to be, that is the question",
            'd': {'nested': "this is not touched, {a}, {b}, {c}"}
        }
        '''

        Note: this function is able to resolve only simple references
        """
        from copy import deepcopy
        mappings = deepcopy(kvmaps) # notice the copy! we don't want to modify the input

        maps_ignored = {}
        for k,v in kvmaps.items():
            if not isinstance(v, str):
                maps_ignored[k] = mappings.pop(k)

        # all those values pure, clean from reference ("{bla}") are already separated
        import re
        mapout = {k:v for k,v in mappings.items()
                      if not re.match('.*{.+}.*', v) }

        cnt = 0
        while len(mapout) < len(mappings):
            cnt += 1
            assert cnt <= len(mappings), "Apparently we are going for an infinite loop here..."
            _reset = set(mappings.keys()) - set(mapout.keys())
            # _aux = {k:mappings[k].format(**mapout) for k in _reset}
            # mapout.update({ k:v for k,v in _aux.items()
            #                 if not re.match('.*{.+}.*', v) })
            for k in _reset:
                try:
                    _aux = { k:mappings[k].format(**mapout) }
                except:
                    continue
                else:
                    mapout.update(_aux)

        # get those maps previously ignored (because they were not strings) and bring back
        mapout.update(maps_ignored)
        return mapout

    return [_solve_self_references(d) for d in dsets]


# Overwrite '_datasets' with parsed/dereferenced version
_datasets = _solve_datasets_references(_datasets)


# Reorganize datasets (that's why I think actually the 'id' field is a bit useless...)
# we will pivot the dataset 'id's (now dereferenced) to datasets keys
def _reorganize_datasets_after_id(dsets: list) -> dict:
    """
    Move key 'id' inside each dset (item) to as "key" in the output dictionary

    Example input:
    '''
    [
        {
            'id': "unique_id",
            'keyword': "value"
        }
    ]
    '''
    , corresponding output:
    '''
    {
        'unique_id': { 'keyword': "value" }
    }
    '''
    """
    from copy import deepcopy
    input_copy = deepcopy(dsets)
    dout = {}
    for dset in input_copy:
        _id = dset.pop('id')
        dout.update({ _id: dset })
    return dout


# Redefine '_datasets' to be a dictionary-of-dictionaries (with 'id' as key)
# instead of a list-of-dictionaries (with 'id' inside each).
# 'id' is gonna be removed/pivot from inside each dictionary to the top-level keys.
_datasets = _reorganize_datasets_after_id(_datasets)


def list():
    for did in _datasets.keys():
        print(did)


# class ResultsSearch:
#     _data = None
#     def to_geojson(self, fileout=None):
#         raise NotImplementedError
#
#     def download(self, outdir=None):
#         raise NotImplementedError
#
#
# class DatasetBase(object):
#     def search(cls, bbox: BBox) -> ResultsSearch:
#         try:
#             res = ode.search(bbox, dataset=cls._datasetid)
#         except:
#             res = ResultsBase()
#         return res
