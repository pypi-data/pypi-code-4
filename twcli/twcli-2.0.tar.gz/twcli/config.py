import ConfigParser
import sys
import os

def init_storage(name='.settings', category='Connection'):
    '''important to use before accessing storage, we always need to think that
    settings were deleted, just so we wont be suprised'''

    settings_path = os.path.expanduser('~/.config/twcli/{0}'.format(name))

    if not os.path.exists(settings_path):
        config = ConfigParser.RawConfigParser()
        config.add_section(category)
        try:
            with open(settings_path, 'wb') as configfile:
                config.write(configfile)
        except IOError:
            try:
                os.mkdir(os.path.expanduser('~/.config/twcli'))
            except IOError:
                print("Conflict with existing settings file or no "
                      "~./config directory!")
                sys.exit(1)
            with open(settings_path, 'wb') as configfile:
                config.write(configfile)

    try:
        settings = ConfigParser.ConfigParser()
        settings.read(settings_path)
    except ConfigParser.ParsingError:
        print('Settings file broken, removing...')
        os.unlink(settings_path)
        return init_storage()
    return settings_path


def save_storage(config, settings_path):
    with open(settings_path, 'wb') as configfile:
        config.write(configfile)


def store_item(value, name, category='Connection'):
    settings_path = init_storage()
    settings = ConfigParser.RawConfigParser()
    settings.read(settings_path)
    try:
        settings.set(category, name, str(value))
    except ConfigParser.NoSectionError:
        settings.add_section(category)
        settings.set(category, name, str(value))
    save_storage(settings, settings_path)


def get_all_items(match, category='Connection'):
    settings_path = init_storage()
    settings = ConfigParser.ConfigParser()
    settings.read(settings_path)
    try:
        items = settings.items(category)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return False
    else:
        retlist = []
        for name, item in items:
            if match in name:
                retlist.append((name, item))
        return retlist


def get_item(name, category='Connection'):
    '''Gets item from local settings file, retuns string or None'''
    settings_path = init_storage()
    settings = ConfigParser.ConfigParser()
    settings.read(settings_path)
    try:
        item = settings.get(category, name, 1)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return False
    else:
        return item


def remove_item(name, category='Connection'):
    settings_path = init_storage()
    settings = ConfigParser.ConfigParser()
    settings.read(settings_path)
    settings.remove_option(category, name)
    save_storage(settings, settings_path)
