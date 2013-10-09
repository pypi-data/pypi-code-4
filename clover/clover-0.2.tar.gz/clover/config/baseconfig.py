from __future__ import absolute_import
import logging
import os


logger = logging.getLogger('clover.config.Config')


class InputError(Exception):
    pass


class ConfigError(Exception):
    pass


class ConfigSyntaxError(Exception):
    def __init__(self, config, original_error, message):
        super(ConfigSyntaxError, self).__init__()
        self.msg = message
        self.config = config
        self.original_error = original_error

    def __str__(self):
        string = ['Syntax error in %s: %s' % self.path, self.msg]
        parent_config = self.config.get_parent()
        if parent_config:
            string.append('included from %s' % parent_config.get_path())
        string.append('%s' % self.original_error)
        return ', '.join(string)


class OptionValidationError(Exception):
    def __init__(self, exception, config, option, value):
        super(OptionValidationError, self).__init__()
        self.exception = exception
        self.config = config
        self.option = option
        self.value = value

    def __str__(self):
        return "Option \"%s\" invalid. (%s)\n%s\nGot: %r" % (
            self.option.name, self.config.filename, self.exception.message, self.value)

class InvalidConfigurationValue(Exception):
    pass

    

class BaseConfig(object):
    """ Represents a full project configuration. 
    """
    options = None

    dir = None
    filename = None
    paths = None
    inputs = None
    
    LINK_REQUIRE = 1
    LINK_INCLUDE = 2
    LINK_PARENT = 3

    def add_link(self, config, link_type):
        self.links.setdefault(link_type, []).append(config)
    
    def __init__(self):
        self.paths = []
        self.inputs = []
        self.option_cache = {}
        self.links = {}

    @property
    def basedir(self):
        raise NotImplementedError

    @property
    def dirty(self):
        raise NotImplementedError

    def has_option(self, item):
        raise NotImplementedError

    def get(self, *args):
        raise NotImplementedError

    option_cache = None

    def read_option(self, option):
        name = option.get_name()

        if name not in self.option_cache:
            self.option_cache[name] = option()

        option_instance = self.option_cache[name]

        logger.debug('Read option %s', name)

        # err for missing required options
        if option.get_required() and not self.has_option(name):
            raise ConfigError("Missing required configuration parameter: %s" % name)

        # return default/None for missing non-required options
        if not self.has_option(name):

            logging.debug('Generating default %s', name)
            if option.has_default():
                return option_instance.get_default(self)
            return None

        value = self.get(name)
        logger.debug(' -> %s', value)

        return value

    def parse(self):
        pass

    def get_id(self):
        raise NotImplementedError

    def get_parents(self):
        raise NotImplementedError

    def set_includes(self, includes):
        """ if the path is relative, calculate from this.basedir
        :param filename: if 
        :return:
        """
        pass


def interpret_path(path, basedir):
    if not path.startswith('/'):
        return os.path.abspath(os.path.normpath(os.path.join(basedir, path)))
    else:
        return os.path.abspath(os.path.expanduser(path))


class InvalidConfigError(Exception):
    pass


def highlight_error(lines, obj):
    string = []

    start_line = obj.start_mark.line
    start_col = obj.start_mark.column
    end_line = obj.end_mark.line
    end_col = obj.end_mark.column

    if end_line == start_line:
        line_string = lines[start_line]
        string.append(line_string[start_col:end_col])

    for line in range(start_line, end_line):
        if line == start_line:
            string.append(line_string[start_col:])
        elif line == end_line:
            string.append(line_string[:end_col])

    return '\n'.join(string)



        
        
        
