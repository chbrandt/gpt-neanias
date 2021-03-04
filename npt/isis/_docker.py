from sh import docker, awk, tail

from npt import log


def containers():
    """
    Return list of container (names) instanciated
    """
    from io import StringIO

    buf = StringIO()
    try:
        tail(awk(docker('ps','-a'), '{print $NF}'), '-n+2', _out=buf)
    except Exception as err:
        log.error(err)

    containers = buf.getvalue().split()
    return containers

list_containers = containers


def restart(name):
    """
    Re/Start a container
    """
    if name in containers():
        docker('start',name)
        return True
    else:
        log.warning(f"No container '{name}' instantiated. Nothing to restart.")
        return False

container_restart = restart
