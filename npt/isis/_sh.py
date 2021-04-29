from npt import log

# import sh

from ._docker import containers as list_containers


class Sh(object):
    """
    Class meant to abstract the underlying Shell/OS layer

    It is similar to the package 'sh' (https://pypi.org/project/sh/) in the
    sense that it "wraps" command-line/shell commands to work seemlessly from
    inside Python.
    Different from pure 'sh' (which this class is based on),
    this class necessarily adds a routing layer: instead of doing `sh.ls('-l')`
    as you would with 'sh', here you have to do `ls = sh.wrap('ls'); ls('-l')`.
    Which *is similar* to 'sh.bare' method, but here is mandatory.

    There are three reasons that justify it:
    * commands are *always* run in a bash login shell,
    * docker containers can be set to seemlessly run commands,
    * a logging handler is set to *always* log the wrapped commands

    In case a (docker) container is used, and volumes are being used for I/O,
    this wrapper also *translates* host URL to corresponding ones inside docker.
    """
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
        """
        Simply start a brand new shell.
        """
        _sh = _set_sh()
        log.debug(_sh)
        self._sh = _sh
        self._maps = None

    @staticmethod
    def log(res):
        log.debug("Exit code: "+str(res and res.exit_code))

    def set_docker(self, name, mappings=None, inspect=False):
        """
        Set running container 'name' to handle exec/commands

        Input:
            name: string
                Name of a running container
            mappings: list, dictionary
                Either a list/tuple mapping host to container paths,
                `` ('path_in_host', 'path_in_container') ``
                or a dictionary where keys are labels/args and values the tuples:
                `` { 'arg': ('path_in_host', 'path_in_container') } ``
        """
        assert name in list_containers()
        self._sh = _set_sh_docker(name)
        self._maps = mappings

    def wrap(self, exec):
        """
        Return a callable wrapping command 'exec'

        This callable (really just a closure around Bash) accepts *any*
        argument(s) or kw-argument(s) you feel like running 'exec' with.

        Input:
            * exec : str
                Command name to wrap (e.g, "echo")
        """
        return _wrap(exec, sh_local=self)


def _set_sh():
    """
    Return a Bash login shell
    """
    from sh import bash
    return bash.bake('--login -c'.split())


def _set_sh_docker(name):
    """
    Return a Bash login shell from "inside" container 'name'

    "Inside" means it will exec whatever (wrapped) command from inside the
    (docker) container in a Bash login shell.
    """
    from sh import docker
    _exec_ = "exec -t {name!s} bash --login -c"
    if name not in list_containers():
        # TODO: together with an option "autorun", start/run container if not yet.
        raise ValueError
    dsh = docker.bake(_exec_.format(name=name).split())
    return dsh


def _map_args(args, map_paths):
    """
    Translate 'args' according to 'map_paths'

    'args' is like:
    ```
    ['dummy-arg', '/Volumes/at_host/bla.txt']
    ```
    And 'map_paths' (given at 'Sh.set_docker()') is like:
    ```
    { 'infile': ('/Volumes/at_host', '/mnt/at_container') }
    ```.
    """
    log.debug(args)
    log.debug(map_paths)
    _args = []
    for arg in args:
        for _host,_cont in map_paths.values():
            arg = arg.replace(_host, _cont)
        _args.append(arg)
    return _args


def _map_kwargs(kwargs, map_paths):
    """
    Translate 'kwargs' values according to 'map_paths' mappings

    'kwargs' is something like:
    ```
    { 'infile' : '/Volumes/at_host/bla.txt' }
    ```.

    And 'map_paths' (given at 'Sh.set_docker()') is like:
    # ```
    # TODO: implement this format!
    # { '/Volumes/at_host' : '/mnt/at_container' }
    # ```
    # or
    ```
    { 'infile': ('/Volumes/at_host', '/mnt/at_container') }
    ```.
    The second form is used only when you want to restrict such mapping/translation
    to a specific command-line argument
    """
    log.debug(kwargs)
    log.debug(map_paths)

    maps = map_paths
    _kw = {}
    if isinstance(maps, dict):
        for key, val in kwargs.items():
            try:
                # Try for the mapping "{ 'infile': ('/Volumes/at_host', '/mnt/at_container') }"
                basepath_host = maps[key][0]
                basepath_cont = maps[key][1]
            except:
                # If not -- either because 'key' doesn't exist or value is not a tuple --
                # just pass key:val forward.
                _kw[key] = val
            else:
                # Translate path from host URL to container's reference.
                _val = val.replace(basepath_host, basepath_cont)
                _kw[key] = _val
    elif isinstance(maps, (list,tuple)):
        for key, val in kwargs.items():
            try:
                basepath_host, basepath_cont = maps
            except:
                _kw[key] = val
            else:
                # Translate path from host URL to container's reference.
                _val = val.replace(basepath_host, basepath_cont)
                _kw[key] = _val
    else:
        # If there is no map defined (for some fucking reason), just map trivially
        # _kw.update(kwargs)
        assert False, "Mapping paths should be defined. This line should never be hit!"

    return _kw


def _wrap(exec, sh_local, log=log):
    """
    Return 'sh' to be called with arguments to 'exec'

    The wrapped 'sh' reports to log.debug and parse the (future) arguments
    to build a string for sh('exec <future-args>').

    Input:
        * exec: string
            command to execute by the container
        * sh_local: Sh
        * log: logging-handler

    Output:
        Return callable/function closure with 'exec' wrapped
    """
    if isinstance(exec, str):
        exec = [exec]

    def _sh(*args,**kwargs):
        """
        Run and return result of 'exec' in 'sh_local' with argument 'args/kwargs'
        """
        v = [f'{v}' for v in args]
        kv = [f'{k}={v}' for k,v in kwargs.items()]
        comm = ' '.join(exec+v+kv)
        log.debug(comm)
        # 'comm' is effectively the full/command-line to run
        return sh_local(comm)

    return _sh


# # Global/Singleton
# sh = Sh()
