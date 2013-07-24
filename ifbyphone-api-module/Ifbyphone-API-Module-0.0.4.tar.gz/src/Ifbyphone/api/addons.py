from base import IfbyphoneApiBase

class Addons(IfbyphoneApiBase):
    
    def list(self):
        """List all purchased Addons for an account
        """
        
        self.options['action'] = 'addons.list'
        return self.call(self.options)
    
    def purchase(self, **kwargs):
        """Purchase an addon for an account
        
        keyword arguments:
        item_id      -- ID number of desired addon
        qty          -- the quantity of the addon
        send_receipt -- set to 1 to send a receipt to account email
        
        """
        self.options.update(kwargs)
        self.options['action'] = 'addons.purchase'
        return self.call(self.options)