from base import IfbyphoneApiBase

class Clicktovr(IfbyphoneApiBase):

    def _call(self, **kwargs):
        """Connect a caller to a virtual receptionist
        
        keyword arguments:
        manu_id       -- ID of the virtual receptionist to use 
        phone_to_call -- phone number to call
        
        """
        
        self.options.update(kwargs)
        self.options['app'] = 'ctvr'
        return self.call(self.options, 'click_to_xyz.php', 'key')