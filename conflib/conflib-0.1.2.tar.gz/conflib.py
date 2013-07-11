# akerl, 2013
# https://github.com/akerl/conflib

'''conflib is designed to simply stacking of configurations
useful when you have defaults & user input, or global and local settings
'''


class Config(object):
    ''' *configs is a stack of dicts or other Config objects
            order flows from least to most 'powerful', for example:
                Config(Defaults, Global, Local)
        validation_dict is passed to self.validate()
    '''
    def __init__(self,
                 *configs,
                 validation_dict={},
                 mismatch_is_fatal=True):
        self.options = {}
        for config in configs:
            if type(config) is dict:
                self.stack(config)
            elif type(config) == type(self):
                self.stack(config.options)
        self.validate(validation_dict)
    ''' new_dict is stacked onto the current options
            in a key conflict, new_dict's value takes precedence
    '''
    def stack(self, new_dict):
        self.options.update(new_dict)
    ''' validation_dict is a dict of key / validation pairs
            validation interpretation is handled in self._do_validation()
    '''
    def validate(self, validation_dict={}):
        for option, validation in validation_dict.items():
            if option in self.options:
                try:
                    self.options[option] = self._do_validation(
                        option, validation, self.options[option])
                except ValueError:
                    print('Validation failed for {0}: {1}'.format(option, self.options[option]))
                    raise
    ''' argument is the key for the option we're dealing with
            (currently not used in the function itself)
        validation is the operator used to determine correctness
            bool converts common boolean things to True/False
            int converts value to an integer
            a list of tuples validates against all items in all tuples
                if there is a match, returns that_tuple[0]
            a list checks for inclusion of vaiue in the list
            a callable will be run, and its value will be returned directly
                this allows you to modify value, but requires that you
                manually raise ValueError if the value is malformed
            anything else will compare type(value) to validation
        value is the provided option to run validation on
    '''
    @staticmethod
    def _do_validation(option, validation, value):
        if validation is bool:
            if value in ['y', 'yes', '1', 1, True]:
                return True
            elif value in ['n', 'no', '0', 0, False]:
                return False
            else:
                raise ValueError
        elif validation is int:
            return int(value)
        elif type(validation) is list:
            if type(validation[0]) is tuple:
                for item in validation:
                    if value in item:
                        return item[0]
                raise ValueError
            elif value in validation:
                return value
            else:
                raise ValueError
        elif type(validation) is type:
            if type(value) is validation:
                return value
            else:
                raise ValueError
        elif hasattr(validation, '__call__'):
            try:
                return validation(value)
            except TypeError:
                raise ValueError
        else:
            raise ValueError

