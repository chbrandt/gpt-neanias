import logging
# fmt="%(levelname)s:%(funcName)s():%(lineno)i: %(message)s"
fmt="%(levelname)s:%(funcName)s(): %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)
log = logging.getLogger()