from base import IfbyphoneApiBase

class Registernumbers(IfbyphoneApiBase):

    def add(self, **kwargs):
        """ Add a registered number to an account
        
        keyword arguments:
        phone       -- number to add
        description -- description of the number
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'registerednumbers.add'
        return self.call(self.options)
        
    def list(self):
        """List all registered numbers
        """
        
        self.options['action'] = 'registerednumbers.list'
        return self.call(self.options)
    
    def remove(self, phone):
        """Remove a registered number
        
        keyword argument:
        phone -- registered number to remove
        
        """
        
        self.options['phone'] = phone
        self.options['action'] = 'registerednumbers.remove'
        return self.call(self.options)