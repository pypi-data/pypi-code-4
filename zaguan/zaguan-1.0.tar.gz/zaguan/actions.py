class BaseActionController(object):
    """Base class for actions that are binded into controllers."""

    def __init__(self, controller):
        self.__controller = controller

    @property
    def controller(self):
        """Returns the controller instance."""
        return self.__controller
