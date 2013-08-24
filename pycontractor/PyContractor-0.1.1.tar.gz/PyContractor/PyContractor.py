import inspect


def whoami():
    return inspect.stack()[1][3]


class PyContractor(object):

    @staticmethod
    def require(condition, message=''):
        """
        :param condition: conditional expression to assert
        :type condition: boolean expression
        :param message: Message to show when the evaluation fails
        :type message: str
        """
        PyContractor()._evaluate('Pre', condition, message)

    @staticmethod
    def require_not_blank(string, message=''):
        """
        :param string: string to assert if it's blank or not
        :type string: str
        :param message: Message to show when the evaluation fails
        :type message: str
        """
        if not string:
            PyContractor()._raiseError('Pre', message, whoami())

    @staticmethod
    def assertExpression(condition, message=""):
        """
        :param condition: conditional expression to assert
        :type condition: boolean expression
        :param message: Message to show when the evaluation fails
        :type message: str
        """
        PyContractor()._evaluate('Assert', condition, message)

    invariant = assertExpression

    @staticmethod
    def ensure(condition, message=""):
        """
        :param condition: conditional expression to assert
        :type condition: boolean expression
        :param message: Message to show when the evaluation fails
        :type message: str
        """
        PyContractor()._evaluate('Post', condition, message)

    def _evaluate(self, AssertionType, condition, message):
        """
        :param AssertionType: Type of assertion in string that will be shown in the Exception message when the assertion
        fails
        :type AssertionType: str
        :param condition: conditional expression to assert
        :type condition: boolean expression
        :param message: Message to show when the evaluation fails
        :type message: str
        """
        if not condition:
            currentFrame = inspect.currentframe()
            currentFrame = inspect.getouterframes(currentFrame, 2)
            self._raiseError(AssertionType, message, currentFrame[1][3])

    def fail(self, message=''):
        """
            This method will always raise an Exception with a message given as parameter
            :param message: message to show when Exception is raised
            :type message: str
        """
        self._raiseError('Fail', message, whoami())

    def _raiseError(self, AssertionType, message, caller):
        """
        :param AssertionType: Type of assertion in string that will be shown in the Exception message when the assertion
        fails
        :type AssertionType: str
        :param message: Message to show when the evaluation fails
        :type message: str
        :param caller: selector of caller
        :type caller: method
        """
        raise Exception("{0}-condition failed: {1}\nTrace was: {2}".format(AssertionType, message, caller))

PRECONDITIONALS = [PyContractor.require, PyContractor.require_not_blank]
POSTCONDITIONALS = [PyContractor.ensure]
CONDITIONALS = [PyContractor.assertExpression]

isPreConditional = lambda (method): method in PRECONDITIONALS
isPostConditional = lambda (method): method in POSTCONDITIONALS
isConditional = lambda (method): method in PRECONDITIONALS+POSTCONDITIONALS+CONDITIONALS