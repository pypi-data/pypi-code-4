import logging

logger = logging.getLogger('to_terminal')
class ExpectedLengthException(Exception):
    
    """A utility Exception thrown when an expected iterated length does not equal
    an actual iterated length
    """
    
    def __init__(self, name, expected, actual):
        """Constructor
        
        ## Arguments:
        
        :name: The name of the variable.
        
        :expected: The expected length.
        
        :actual: The actual length.
        
        """
        super(ExpectedLengthException, self).__init__(
            'Expected %s to be of length %d. Instead, got a length of %d.'%(
                name, expected, actual) )