import logging

_sep = ":"
_fmt = f"%(levelname)s{_sep}%(funcName)s(){_sep}%(message)s"

logging.basicConfig(level=logging.INFO, format=_fmt)

log = logging.getLogger()

log.fair = lambda msg:log.info(f"[fair]{_sep}" + msg)
