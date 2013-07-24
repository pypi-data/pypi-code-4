from base import IfbyphoneApiBase

class Recordings(IfbyphoneApiBase):
    
    def download(self, **kwargs):
        """Download a specific recording
        
        keword arguments:
        type        -- type of app to download from | 'findme'
        sid         -- session ID of the call 
        format      -- 'wav' or 'mp3'
        sample_rate -- audio rate of streaming data 
                       values: 8000 (default), 11000 (wav only), 22050, 44100
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'recording.download'
        return self.call(self.options)
        
    def list(self, _id):
        """ List available recordings
        
        keyword argument:
        _id -- unique app ID of findme to list recordings from
        
        """
        
        self.options['type'] = 'findme'
        self.options['id'] = _id
        self.options['action'] = 'recording.list'
        return self.call(self.options)
        
    def remove(self, **kwargs):
        """Remove a recorded call file 
        
        keyword arguments:
        sid        -- session ID of the call 
        delete_now -- set to 1 to delete file immediately
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'recording.remove'
        return self.call(self.options)
        
    def upload(self, **kwargs):
        """Upload an audio file for use in account
        
        keyword arguments:
        type -- type of building block the file is for:
                general - General audio for SurVo custom audio prompts
                survo   - SurVo prompts
                voting  - Prompts for VoteByPhone
                holdmusic - Hold music for Find Me
                vmail   - Voice mail greetings
                whisperaudio - Whisper audio for Find Me
                prompts - Advanced Audio prompts for Find Me
        path -- public URL to file 
        id   -- required for 'survo' and 'vmail' types. The id is the 
                Building Block ID for the appropriate SurVo or Voice 
                Mail box to upload the file for
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'recording.upload'
        return self.call(self.options)