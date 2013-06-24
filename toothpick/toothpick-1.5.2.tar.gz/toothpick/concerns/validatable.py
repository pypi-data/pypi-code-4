from toothpick import hooks

class Validatable(object):

    @hooks.hook_provider('validation')
    def valid(self):
        '''
        Runs all the validations associated with this class against this
        instance, and returns true if no errors are set on this instance, false
        otherwise.  The `Errors` object on this instance is cleared before the
        validations are run.  All validations are run regardless of
        intermediate failures.
        '''
        self.errors.clear()
        [validator(self) for validator in self._validators]
        return not(self.errors)


