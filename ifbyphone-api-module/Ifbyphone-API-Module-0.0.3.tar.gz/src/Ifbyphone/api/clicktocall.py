from base import IfbyphoneApiBase

class Clicktocall(IfbyphoneApiBase):

    def _call(self, **kwargs):
        """ Initiate a phone call connecting two parties
        
        keyword arguments:
        type -- values: 1 Call "phone_to_call" value first 
                        2 = Call "id" first
        id   -- a registered number or the main number of the 
                account if using Public key, any number if using API key
        phone_to_call -- number to call 
        page -- reference for what web page the click-to-call was on
                this value will display in the click to call report
        ref  -- used for individual use (can be any string)
                this value will display in the click to call report
        
        first_callerid  -- caller ID for the first leg of the call 
        second_callerid -- caller ID for the second leg of the call 
        
        """
        
        self.options.update(kwargs)
        self.options['app'] = 'ctc'
        self.call(self.options, 'click_to_xyz.php', 'key')