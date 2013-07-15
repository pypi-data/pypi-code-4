from base import IfbyphoneApiBase

class Cost(IfbyphoneApiBase):

    def get_surcharge(self, phone_list=None):
        """ Get the surcharge cost for an international phone number
        
        keyward argument:
        phone_list -- Bar "|" delimited list of phone numbers to get surcharges for. 
                      All phone numbers must start with '011' 
        """
        if phone_list is not None:
            self.options['phone_list'] = phone_list
        
        self.options['action'] = 'cost.get_surcharge'
        return self.call(self.options)