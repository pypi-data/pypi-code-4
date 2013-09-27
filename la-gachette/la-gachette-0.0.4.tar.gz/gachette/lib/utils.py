import os
from fabric.api import run, settings
import yaml


def get_config(config_file):
    """
    Use to monkey patch fabric loading of settings to use yaml file
    """
    if os.path.exists(config_file):
        return yaml.load(file(config_file, 'r'))

    return {}

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

def expand_dotted_keys(array):
    """
    Expand the dotted keys in a dict: {"foo.bar":5} => {"foo": {"bar": 5}} 
    """
    new_array = {}
    for k,v in array.iteritems():
        new_array = deep_merge(new_array, dict_tuple_dotted(k,v))
    return new_array

def dict_tuple_dotted(k, v):
    """
    Create a dictionary out of a tuple with dotted key.
    ("fii.bot", "toto") => {"fii": {"bot": "toto"}}
    """
    d = k.split(".", 1)
    if len(d) == 1:
        return dict([(d[0], v)])
    else:
        return dict([(d[0], dict_tuple_dotted(d[1], v))])


def deep_merge(params, default):
    """ 
    Deep merge of dictionaries.
    """
    if isinstance(params,dict) and isinstance(default,dict):
        for k,v in default.iteritems():
            if k not in params:
                params[k] = v
            else:
                params[k] = deep_merge(params[k],v)
    return params
