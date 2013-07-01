from base import IfbyphoneApiBase

class Clicktovoicemail(IfbyphoneApiBase):

    def _call(self, **kwargs):
        """Connect a caller to a voice mail
        
        keyword arguments:
        vmail_box_id  -- ID of the voice mail to use 
        phone_to_call -- phone number to call 
         
        """
        
        self.options.update(kwargs)
        self.options['app'] = 'ctvm'
        return self.call(self.options, 'click_to_xyz.php', 'key')