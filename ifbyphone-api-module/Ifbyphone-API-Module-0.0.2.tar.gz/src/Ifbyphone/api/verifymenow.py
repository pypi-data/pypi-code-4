from base import IfbyphoneApiBase

class Verifymenow(IfbyphoneApiBase):
    
    def get_recording(self, **kwargs):
        """Retrieve a recording from a verifymenow smart form
        
        keyword arguments:
        format      -- 'wav' 'mp3'
        verify_id   -- Unique ID for the verifymenow application
        sid         -- unique session ID of the call associated with recording
        sample_rate -- audio rate of streaming data | 
                       values: 8000 (default), 11000 (wav only), 22050, 44100
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'verifymenow.get_recording'
        return self.call(self.options)
        
    def verify(self, **kwargs):
        """Initiate a call to recipient to be verified
        
        keyword arguments:
        verify_id    -- unique ID of the verifymenow app to use 
        phone_number -- recipient of the call 
        pin          -- digits the recipient must enter to be verified
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'verifymenow.verify'
        return self.call(self.options)