import yaml


def get_yaml_config(config_file, env="default"):
    # open config file and load yaml.
    stream = file(config_file, 'r')
    data = yaml.load(stream)

    # if no default, then move on
    if 'default' not in data:
        yield data
    else:
        yield data['default']

        for key, value in data.iteritems():
            if key != 'default':
                yield _merge(data[key], data['default'])


def load_yaml_config(config_file, env="default"):
    """ Read a yaml file and extract the configuration. """

    # open config file and load yaml.
    stream = file(config_file, 'r')
    data = yaml.load(stream)

    # if no default, then move on
    if 'default' not in data:
        return data

    # return the value for the right environment.
    if env == "default":
        final_data = data["default"]
    else:
        final_data = _merge(data[env], data['default'])

    return final_data


def _merge(params, default):
    """ Deep merge of dictionary. """
    if isinstance(params,dict) and isinstance(default,dict):
        for k,v in default.iteritems():
            if k not in params:
                params[k] = v
            else:
                params[k] = _merge(params[k],v)
    return params


def print_pretty(d, indent=0):
    """ Pretty print of nested dictionary """
    for key, value in d.iteritems():
        print '\t' * indent + str(key)
        if isinstance(value, dict):
            print_pretty(value, indent+1)
        else:
            print '\t' * (indent+1) + str(value)


def flatten_dict(init, lkey=''):
    ret = {}
    for rkey,val in init.items():
        key = lkey+rkey
        if type(val) is dict:
            ret.update(flatten_dict(val, key+'_'))
        else:
            ret[key] = val
    return ret
