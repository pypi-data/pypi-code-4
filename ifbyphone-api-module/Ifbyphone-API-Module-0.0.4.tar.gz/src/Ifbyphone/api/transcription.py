from base import IfbyphoneApiBase

class Transcription(IfbyphoneApiBase):

    def create(self, **kwargs):
        """Create a transcription of an audio file
        
        keyword arguments:
        path -- path to the audio file to upload
        type -- type of transcription:
            1 - Fully automated computer transcription.
            2 - Automated with human assistance. If the 
                computer cannot accurately identify a 
                word or phrase it will send just that 
                snippet to a human operator for translation.
            3 - Fully human transcription
            
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'transcription.create'
        return self.call(self.options)
        
    def get(self, **kwargs):
        """Get an existing transcription
        
        keyword arguments:
        id         -- ID of a specific transcription
        start_date -- use for retrieving a list within a date range
        end_date   -- use for retrieving a list within a date range
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'transcription.get'
        return self.call(self.options)