from fabric.api import run, settings


def prepare_folder(folder, clean=True):
    """
    Create folder if does not exist and set up owner properly.
    """
    with settings(warn_only=True):
        new_folder = run("test -d %s" % folder).failed

        if new_folder:
            run("mkdir -p %s" % (folder))

        if not new_folder and clean:
            run("rm -rf %s/*" % folder)


def build_host(host):
    """
    Returns a fabric settings manager with the host_string setting set to the
    given host.

    :param host: String with the build host name with the form
        ``[user@]host[:port]``
    """
    return settings(host_string=host)
