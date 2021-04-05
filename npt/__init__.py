"""
NEANIAS Planetary Tools (NPT)

This tools are meant to support the data handling of Planetary group
of the H2024 NEANIAS project.
You'll find here tools to search, download and process Planetary data.
"""
from . import _log as log
# from ._db import db

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
