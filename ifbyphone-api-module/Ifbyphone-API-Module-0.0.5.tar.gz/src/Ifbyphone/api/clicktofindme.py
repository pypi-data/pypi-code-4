from base import IfbyphoneApiBase

class Clicktofindme(IfbyphoneApiBase):

    def _call(self, **kwargs):
        """Connect a caller to a number defined in a findme application
        
        keyword arguments:
        phone_to_call   -- phone number to initiate the call to
        findme_id       -- ID of the findme used in the call 
        type            -- '1': regular findme '2': reverse findme
        no_answer_email -- address to send an email if no answer
        no_answer_sms   -- number to send an SMS if no answer
        no_answer_url   -- URL to send xml data if no answer
        no_answer_phone -- phone number to transfer call if no answer
        
        """
        
        self.options.update(kwargs)
        self.options['app'] = 'ctf'
        return self.call(self.options, 'click_to_xyz.php', 'key')