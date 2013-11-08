def str_to_bool(s):
    """Transform a string to boolean.

    :param s: the value to transform as boolean
    :type s: str
    :return: the given is as bool
    :rtype: boolean
    """
    if s == 'false':
        return False
    if s == 'true':
        return True
    raise Exception('Unable to cast as bool %s' % s)


def parse_settings(settings, mapping, key=None, prefix=None):
    """Get the value defined in settings according to the given params.

    :param settings: the config settings
    :type settings: pyramid.registry.Registry.settings
    :param mapping: contains information to know which values should be taken
                    in settings.
    :type mapping: dict
    :param key: if we have many keys in mapping, give which one should be used
    :type key: str
    :param prefix: the prefix of the setting name in settings
    :type prefix: str

    :return: the settings for the given params
    :rtype: dict
    """

    local_mapping = mapping
    if key:
        if key not in mapping:
            raise Exception('No settings defined for %s' % key)
        local_mapping = mapping[key]

    dic = {}
    for k, convert, required, default in local_mapping:
        setting_key = '.'.join(filter(bool, [prefix, key, k]))
        value = settings.get(setting_key)
        if not value:
            if required:
                if default is None:
                    raise AttributeError('%s not defined' % setting_key)
                value = default
            elif default is None:
                # Use the default of the authentication function
                continue
            else:
                value = default
        elif convert:
            value = convert(value)
        dic[k] = value
    return dic
