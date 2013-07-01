from base import IfbyphoneApiBase

class Voicemail(IfbyphoneApiBase):

    def create(self, **kwargs):
        """Create a new voice mail box
        
        keyword arguments:
        name -- name of the voic mail app 
        pin  -- 4 digit value used to access messages via phone
        email_address -- email address messages will be sent to
        send_email    -- bool | 0 false, 1 true 
        envelope      -- bool | read back time, date, etc
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'vmail.createbox'
        return self.call(self.options)
        
    def delete(self, _id):
        """Delete an existing voice mail application
        
        keyword argument:
        _id -- ID of voice mail box to be deleted
        
        """
        
        self.options['box_id'] = _id
        self.options['action'] = 'vmail.deletebox'
        return self.call(self.options)
        
    def deletemessage(self, **kwargs):
        """Delete a single message
        
        keyword arguments:
        box_id     -- voice mail app associated with message
        message_id -- unique ID of the message to be deleted
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'vmail.deletemessage'
        return self.call(self.options)
        
    def getmessagebyid(self, _id):
        """Retrieve voice mail message by it's unique ID
        
        keyword argument:
        _id -- unique ID if the message to retrieve
        
        """
        
        self.options['vmail_id'] = _id
        self.options['action'] = 'getmessagebyid'
        return self.call(self.options)
        
    def getmessagebysid(self, **kwargs):
        """Retrieve a voice mail message by session ID
        
        keyword arguments:
        vmail_sid -- session ID associated with message 
        vmail_id  -- voice mail app ID associated with message
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'getmessagebysid'
        return self.call(self.options)
        
    def getmessages(self, **kwargs):
        """Retrieve all messages for a voice mail box
        
        keyword arguments:
        box_id    -- unique ID of the voice mail box
        greetings -- retrieve greeting messages | bool 
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'vmail.getmessages'
        return self.call(self.options)
        
    def recordgreeting(self, **kwargs):
        """Record a voice mail greeting 
        
        keyword arguments:
        box_id         -- unique ID of voice mail for the greeting
        recording_type -- 'greeting' for 'vacation'
        phone_to_call  -- number to call to record greeting
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'vmail.recordgreeting'
        return self.call(self.options)