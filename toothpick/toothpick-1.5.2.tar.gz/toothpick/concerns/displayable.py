import inflection

class Displayable(object):

    @classmethod
    def _model_name(cls):
        '''Returns the name of this class as a string'''
        return cls.__name__

    @classmethod
    def _model_display_name(cls):
        return cls._model_name()

    @classmethod
    def _view_name(cls, operation):
        '''Returns the name of a view to perform the given operation on this
        model'''
        # TODO: validate this against actual views
        name = inflection.underscore(cls._model_name())
        if operation in ['list']: # add any other plural operation here
            name = inflection.pluralize(name)

        return "%s_%s" % (operation, name)

    def _view_args(self, operation="show", **extensions):
        '''This method returns a dictionary of keyword arguments meant
        to be passed to a view method.  It takes an argument `operation`
        to allow different arguments to be sent to different actions.

        The keys of the dictionary returned by this function should
        correspond with the arguments to the model's view function
        involving the given operation.'''
        return dict(self._default_view_args().items()
                    + extensions.items())

    def _default_view_args(self):
        return { (inflection.underscore(self._model_name()) + "_id"): self.id }
    
    def _display_name(self):
        '''Generates a user-friendly display string'''
        return "%s %s" % (self._model_name(), self.id)

    def _display_title(self):
        '''Used in page titles, defaults to aliasing #_display_name()'''
        return self._display_name()




