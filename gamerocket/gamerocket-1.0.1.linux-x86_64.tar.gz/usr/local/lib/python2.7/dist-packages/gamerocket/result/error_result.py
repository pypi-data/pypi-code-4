class ErrorResult(object):
    
    def __init__(self, attributes):
        self.error = attributes['error']
        self.error_description = attributes['error_description']
    
    def __repr__(self):
        return "<%s: '%s'>" % (self.error, self.error_description)
    
    @property
    def is_success(self):
        
        return False