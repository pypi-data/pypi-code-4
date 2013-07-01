from base import IfbyphoneApiBase

class Numbers(IfbyphoneApiBase):

    def order(self, **kwargs):
        """Order a local or tollfree number
        
        keword arguments:
        quantity      -- amount of numbers to purchaase
        type          -- 'local' , 'tollfree' or 'true800
        searchc       -- must be either a 3 digit number 
                         to search by area code only or 6 
                         digit number to search by area 
                         code + exchange.
        fill_quantity -- set this parameter to 1 if you only 
                         want to complete an order if we can meet 
                         the quantity selected. Set this parameter 
                         to 0 if you want to order as many numbers 
                         as we have in our inventory up to the 
                         quantity selected
                         
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'numbers.order'
        return self.call(self.options)
        
    def remove(self, number):
        """Remove a number from an account
        
        keyword argument:
        number -- the number to be removed
        
        """
        
        self.options['number'] = number
        self.options['action'] = 'numbers.remove'
        return self.call(self.options)
        
    def search(self, **kwargs):
        """Search for numbers available for order
        
        keyword arguments:
        type     -- type of number | 'local' or 'tollfree'
        quantity -- max numbers to return | max: 50
        value    -- for local numbers, the first 3 or 6 digits
        
        """    
        
        self.options.update(kwargs)
        self.options['action'] = 'numbers.search'
        return self.call(self.options)