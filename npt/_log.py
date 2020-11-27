import logging

_sep = ":"
_fmt = f"%(levelname)s{_sep}%(funcName)s(){_sep}%(message)s"

logging.basicConfig(level=logging.DEBUG, format=_fmt)

log = logging.getLogger()

def _log_fair(msg):
    log.debug("[fair]{!s}{!s}".format(_sep, msg))

log.fair = _log_fair
