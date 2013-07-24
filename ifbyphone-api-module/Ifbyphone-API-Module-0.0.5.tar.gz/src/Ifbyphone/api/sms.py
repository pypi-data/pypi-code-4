from base import IfbyphoneApiBase

class Sms(IfbyphoneApiBase):
    
    def send(self, **kwargs):
        """ Send an outbound SMS message 
        
        keyword arguments:
        to      -- number to receive SMS message
        from    -- Ifbyphone enabled SMS number
        message -- SMS message 
        
        """
        
        self.options['to'] = kwargs['to']
        self.options['from'] = kwargs['from_']
        self.options['message'] = kwargs['message']
        self.options['action']  = 'sms.send_message'
        return self.call(self.options)
    
    def delete_message(self, msg_id):
        """ Delete a specific SMS messages
        
        keyword arguments:
        msg_id -- unique ID of SMS message
        
        """
        
        self.options['msg_id'] = msg_id
        self.options['action'] = 'sms.delete_message'
        return self.call(self.options)
        
    def get_message(self, msg_id):
        """ Retrieve a specific SMS message
            
        keyword arguments:
        msg_id -- unique ID of SMS message
        
        """
        
        self.options['msg_id'] = msg_id
        self.options['action'] = 'sms.get_message'
        return self.call(self.options)
    
    def get_messages(self, **kwargs):
        """ Retrieve all SMS messages within a date range
        
        keyword arguments:
        number     -- the phone number associates with messages
        start_date -- the dtarting date (yyyy-mm-dd)
        end_date   -- the ending date (yyyy-mm-dd)
            
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'sms.get_messages'
        return self.call(self.options)
    
    def get_numbers(self):
        """ Retrieve all SMS enabled numbers for an account
        """
        
        return self.call(self.options)
        
    def register_number(self, **kwargs):
        """ Register a number to send and receive SMS
        
        keyword arguments:
        number -- phone number to register
        url    -- url to submit inbound SMS post data
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'sms.register_number'
        return self.call(self.options)
        
    def unregister_number(self, number):
        """ Un-register an SMS enabled phone number
        
        keywork arguments:
        number -- phone number to un-register
        
        """
        self.options['number'] = number
        self.options['action'] = 'sms.unregister_number'
        return self.call(self.options)
        