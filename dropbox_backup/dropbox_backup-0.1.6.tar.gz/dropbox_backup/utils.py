import hashlib, math

def filesizeformat(bytes, precision=2):
    """Returns a humanized string for a given amount of bytes"""
    bytes = int(bytes)
    if bytes is 0:
        return '0o'
    log = math.floor(math.log(bytes, 1024))
    return "%.*f%s" % (
        precision,
        bytes / math.pow(1024, log),
        ['o', 'Ko', 'Mo', 'Go', 'To','Po', 'Eo', 'Zo', 'Yo']
        [int(log)]
    )

def md5_checksum(filepath):
    fp = open(filepath, 'rb')
    md5 = hashlib.md5()
    md5.update(fp.read().encode('base64'))
    checksum = md5.hexdigest()
    fp.close()
    return checksum

def get_config_option(config, section, option=None, boolean=False, fallback=None):
    if config.has_section(section):
        if option is None:
            return config.items(section)
        elif config.has_option(section, option):
            return config.get(section, option) if boolean == False else config.getboolean(section, option)
    return fallback