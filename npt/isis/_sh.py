from npt import log

# import sh

from ._docker import containers as list_containers


def _set_sh():
    from sh import bash
    return bash.bake('--login -c'.split())


def _set_sh_docker(name):
    from sh import docker
    _exec_ = "exec -t {name!s} bash --login -c"
    if name not in list_containers():
        # start/run container
        raise ValueError
    dsh = docker.bake(_exec_.format(name=name).split())
    return dsh


def _map_args(args, map_paths):
    log.debug(args)
    log.debug(map_paths)
    _args = []
    for arg in args:
        for _host,_cont in map_paths.values():
            arg = arg.replace(_host, _cont)
        _args.append(arg)
    return _args


def _map_kwargs(kwargs, map_paths):
    log.debug(kwargs)
    log.debug(map_paths)
    maps = map_paths
    _kw = {}
    for key, val in kwargs.items():
        try:
            basepath_host = maps[key][0]
            basepath_cont = maps[key][1]
        except:
            _kw[key] = val
        else:
            # those mappings are paths
            _val = val.replace(basepath_host, basepath_cont)
            _kw[key] = _val
    return _kw


def _wrap(exec, sh_local, log=log):
    """
    Return 'sh' to be called with arguments to 'exec'

    The wrapped 'sh' reports to log.debug and parse the (future) arguments
    to build a string for sh('exec <future-args>').

    Args:
        exec: string
            command to execute by the container
        sh_local: Sh
        log: logging-handler
    """
    if isinstance(exec, str):
        exec = [exec]
    def _sh(*args,**kwargs):
        v = [f'{v}' for v in args]
        kv = [f'{k}={v}' for k,v in kwargs.items()]
        comm = ' '.join(exec+v+kv)
        log.debug(comm)
        return sh_local(comm)
    return _sh


class Sh(object):
    _sh = None
    _maps = None
    def __init__(self):
        self.reset()

    def __call__(self, *args, **kwargs):
        log.debug(args)
        log.debug(kwargs)
        if self._maps:
            args = _map_args(args, self._maps)
            kwargs = _map_kwargs(kwargs, self._maps)
        return self._sh(*args, **kwargs)

    def reset(self):
        _sh = _set_sh()
        log.debug(_sh)
        self._sh = _sh

    @staticmethod
    def log(res):
        log.debug("Exit code: "+str(res and res.exit_code))

    def set_docker(self, name, mappings=None):
        """
        Args:
            name: <string>
                name of a running container
            mappings: {'arg':('host','container')}
                dictionary with tuples mapping host to container paths
        """
        assert name in list_containers()
        self._sh = _set_sh_docker(name)
        self._maps = mappings

    def wrap(self, exec):
        return _wrap(exec, sh_local=self)

    bake = wrap


# Global/Singleton
sh = Sh()
