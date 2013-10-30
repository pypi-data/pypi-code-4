"""module sense

Sense
=====

Utilities for IPython on Sense.

Support: support@senseplatform.com
"""
import os
import IPython
import requests
import futures
import simplejson

__all__ = ["install", "network_info", "get_auth",
           "launch_workers", "list_workers", "get_master", "stop_workers"]


THREAD_POOL_SIZE = 10

def expand_cli_arguments(arg, value=None):
    if len(arg) == 1:
        dashed_args = "-" + arg
        if value is not None:
            return dashed_args + " " + value
    else:
        dashed_args = "--" + arg
        if value is not None:
            return dashed_args + "=" + value
    return dashed_args


def install(package_name, flags=[], arguments={}):
    """install

    Description
    -----------

    Installs the named package to the current project using `pip. <http://www.pip-installer.org/>`_

    Parameters
    ----------
    package_name: str 
        The name of the `Python package <https://pypi.python.org/pypi>`_ to install.
    flags: list, optional
        Command line flags for pip.
    arguments: list, optional
        Command line agruments for pip.

    Details
    -------

    >>> sense.install("beautifulsoup")

    The flags list, if provided, will be passed to pip as flags.
    For example,

    >>> ["U", "use-mirrors"]

    translates to

    >>> -U --use-mirrors

    The arguments dict, if provided, will be passed to pip as
    command-line arguments. For example,

    >>> {"d": "./downloads", "mirrors": "http://URL"}

    translates to

    >>> -d ./downloads --mirrors=http://URL
    """
    flag_string = " ".join([expand_cli_argument(v) for v in flags])
    arg_string = " ".join([expand_cli_argument(k, v)
                           for k, v in arguments.iteritems()])
    os.system("pip install %s --user" %
              package_name + " " + flag_string + " " + arg_string)


def get_auth():
    """get_auth

    Description
    -----------

    Returns the username and password to use with the `Sense REST API. <https://help.senseplatform.com/api/rest>`_

    Returns
    -------
    dict
        A dict with keys 'user' and 'password'.

    Details
    -------

    On Sense, this function will just work. If you use it locally, you'll
    need to set either SENSE_API_KEY or SENSE_USERNAME and SENSE_PASSWORD
    in the environment.
    """
    if ("SENSE_USERNAME" in os.environ) and ("SENSE_PASSWORD" in os.environ):
        return {"user": os.environ["SENSE_USERNAME"], "password": os.environ["SENSE_PASSWORD"]}
    elif "SENSE_API_KEY" in os.environ:
        return {"user": os.environ["SENSE_API_KEY"], "password": ""}
    else:
        raise RuntimeError(
            "Either set environment variable SENSE_API_KEY, or else SENSE_USERNAME and SENSE_PASSWORD")


def network_info():
    """network_info

    Description
    -----------

    Returns the current dashboard's networking information.

    Returns
    -------
    dict
        A dict with keys dns_public, public_port_mapping, ssh_password
        and project_ip. public_port_mapping is a dict whose keys and
        values are integers.

    Details
    -------

    The project IP address is only accessible to other dashboards in the
    same project. Any port can be accessed via the project IP address.

    The public DNS, public port mapping and SSH password tell you how
    the current dashboard can be contacted from outside the project.

    Only ports that are keys of public_port_mapping can be accessed via
    the public DNS. However, contacting dashboards via the public DNS
    gives better network performance than the project IP.

    If you run a service on port 3000, for example, it
    can be accessed from outside the dashboard on the public DNS on port
    ``public_port_mapping[3000]``.

    The dashboard's SSH daemon is listening on the public DNS on port
    ``public_port_mapping[22]``, and will accept the SSH password for user ``sense``.
    """
    port_mapping = {}
    i = 1
    while ("SENSE_PORT" + str(i)) in os.environ:
        port_mapping[int(os.environ["SENSE_PORT" + str(i)])] = int(
            os.environ["SENSE_PUBLIC_PORT" + str(i)])
        i = i + 1
    port_mapping["22"] = os.environ["SENSE_PUBLIC_SSH_PORT"]
    return {
        "public_dns": os.environ["SENSE_PUBLIC_DNS"],
        "public_port_mapping": port_mapping,
        "ssh_password": os.environ["SENSE_SSH_PASSWORD"],
        "project_ip": os.environ["SENSE_PROJECT_IP"]
    }


def get_master_id():
    if os.environ["SENSE_MASTER_ID"] == "":
        master_id = os.environ["SENSE_DASHBOARD_ID"]
    else:
        master_id = os.environ["SENSE_MASTER_ID"]
    return master_id


def get_base_url():
    return os.environ["SENSE_PROJECT_URL"] + "/dashboards"


def launch_workers(n, size=0, engine="sense-ipython-engine", script="", code="", env={}):
    """launch_workers

    Description
    -----------

    Launches worker dashboards into the current cluster.

    Parameters
    ----------
    n: int
        The number of dashboards to launch.
    size: int, optional
        The dashboard size, 0 to 16.
    engine: str, optional
        The name of the `npm <http://npmjs.org>`_ module to use as the engine.
    script: str, optional
        The name of a Python source file the dashboard should execute as soon as it starts up.
    code: str, optional
        Python code the dashboard should execute as soon as it starts up. If script is specified, code will be ignored.
    env: dict, optional
        Environment variables to set in the dashboard.

    Returns
    -------
    list
        A list of dashboard dicts of the form described in the `REST API. <http://help.senseplatform.com/api/rest#retrieve-dashboard>`_
    """

    request_body = {
        "engine": engine,
        "size": size,
        "script": script,
        "code": code,
        "env": env,
        "master_id": get_master_id()
    }
    url = get_base_url()
    auth = get_auth()

    headers = {'Content-type': 'application/json','Accept': 'application/json'}

    # The n launch requests are done concurrently in a thread pool for lower                                                 
    # latency.                                                                                                               
    def launch_worker(i):
        return requests.post(url, data=simplejson.dumps(request_body), auth=(auth["user"], auth["password"]), headers=headers).json()
    pool = futures.ThreadPoolExecutor(THREAD_POOL_SIZE)
    responses = [pool.submit(launch_worker, i) for i in xrange(n)]
    return map(lambda x: x.result(), futures.wait(responses)[0])


def list_workers():
    """list_workers

    Description
    -----------

    Returns all information on all the workers in the current cluster.

    Returns
    -------
    list
        A list of dicts of the form described in `the REST API. <http://help.senseplatform.com/api/rest#retrieve-dashboard>`_
    """
    master_id = get_master_id()
    auth = get_auth()
    url = get_base_url() + "/" + os.environ["SENSE_DASHBOARD_ID"] + "/workers"
    return requests.get(url, auth=(auth["user"], auth["password"])).json()

def get_master():
    """get_master

    Description
    -----------

    Returns information on the current dashboard's master.

    Returns
    -------
    dict
        A dict of the form described in `the REST API. <http://help.senseplatform.com/api/rest#retrieve-dashboard>`_
    """
    master_id = get_master_id()
    auth = get_auth()
    url = get_base_url() + "/" + str(master_id)
    return requests.get(url, auth=(auth["user"], auth["password"])).json()


def stop_workers(*ids):
    """stop_workers

    Description
    ----------

    Stops worker dashboards in the current cluster.

    Parameters
    ----------
    ids: int, optional
        The id numbers of the worker dashboards to stop. If not provided, all worker
        dashboards in the cluster will be stopped.

    Returns
    -------
    list
        A list of dicts of the form described in `the REST API. <http://help.senseplatform.com/api/rest#retrieve-dashboard>`_
    """
    if len(ids) == 0:
        ids = [worker["id"] for worker in list_workers()]
        if len(ids) == 0:
            return
        return stop_workers(*ids)
    else:
        base_url = get_base_url()
        auth = get_auth()

        # The stop requests are done concurrently in a thread pool for
        # lower latency.
        def stop_worker(id):
            return requests.put(base_url + "/" + str(id) + "/stop", auth=(auth["user"], auth["password"]))

        pool = futures.ThreadPoolExecutor(THREAD_POOL_SIZE)

        responses = [pool.submit(stop_worker, id) for id in ids]
        return map(lambda x: x.result(), futures.wait(responses)[0])
