from base import IfbyphoneApiBase

class Findme(IfbyphoneApiBase):

    def add_number(self, **kwargs):
        """ Add numbers to an existing findme
        
        keyward arguments:
        findme_id    -- ID of findme to add numbers to
        phone_number -- phone number to add to findme
        
        """
        self.options.update(kwargs)
        self.options['action'] = 'findme.add_number'
        return self.call(self.options)
        
    def create(self, **kwargs):
        """ Create a findme
        
        keyword arguments:
        name              -- name of the findme
        list_type         -- type of findme | 1: individual, 
                             2: customer service huntgroup
        loop_count        -- number of times to loop findme list 
        distribution_type -- How calls reach list. Values: 1, randomize; 2, 
                             round robin. Default: traverse list sequentially
        record            -- record calls
        screen_method     -- Screen caller for information before attempting to connect caller. 
                             Values: 0=Record callers name (default), 1=Use value in whisper_phrase 
                             as TTS, 2=Use value in whisper_audio. The whisper_audio value must 
                             be a file name for an existing whisper message in your account
        screen_prompt     -- TTS screening message
        dtmf_only         -- Requires person answering to use keypad to accept call. 
                             Values: 1, DTMF Only; 0, speech and DTMF 
        holdmusic         -- Audio file to play to caller as caller waits for destination to answer. 
                             Audio file must be in the account "holdme" directory. 
                             Default: Our standard audio file
        holdrepeat        -- How often the hold message is played to the caller. Values: 0, 
                             only once per Find Me session; 1, only once between each attempt 
                             to connect to a destination; 2, repeat continuosly between each 
                             connection attempt: default
        timeout           -- Number of seconds to ring each destination before attempting 
                             next destination (or end action). Values: 10-60. Default is 30
        whisper_phrase    -- Phrase spoken to person who answers phone, used when 
                             call screening is not enabled. Default: no phrase
        findme_action     -- Action to take if Find Me reaches end of list
        findme_action_parameter -- Building Block ID if required by End of List Action
        advanced_audio_id -- If you have already configured an Advanced Audio Prompt Set in another 
                             Find Me you can use that set ID here. Advanced Prompt 
                             sets are specific to the Find Me Type
        numbers           -- Phone numbers to add to the Find Me. Can either be a single number 
                             or a comma-separated list of numbers. Must be a numeric 
                             string without any punctuation.
        auto_accept       -- How and when to auto-accept the call. Valid values are 0-4:
                             0 - Disabled (default)
                             1 - Auto-accept on first answered call
                             2 - Auto-accept on the last number tried with screening
                             3 - Auto-accept on the last number tried without screening
        simul             -- Number of calls to make simultaneously. Maximum is defined by your account type                             
        whisper_audio     -- The name of an audio file in your Whisper Phrase Audio files folder
        """
        self.options.update(kwargs)
        self.options['action'] = 'findme.create'
        return self.call(self.options)
        
    def delete(self, findme_id):
        """ Delete a findme
        
        keyword argument:
        findme_id -- ID of the findme to delete
        
        """
        self.options['findme_id'] = findme_id
        self.options['action'] = 'findme.delete'
        return self.call(self.options)
    
    def delete_number(self, **kwargs):
        """Delete a number from a findme
        
        keyword arguments:
        findme_id        -- ID of the findme where number is deleted
        findme_number_id -- ID of number to remove
        
        """
        self.options.update(kwargs)
        self.options['action'] = 'findme.delete_number'
        return self.call(self.options)
    
    def delete_recorded_call(self, **kwargs):
        """ Delete a findme recorded call
        
        keyword arguments:
        findme_id      -- ID of the findme that made the recording
        recording_name -- file name of the recording to delete
        
        """
        self.options.update(kwargs)
        self.options['action'] = 'findme.delete_recorded_call'
        return self.call(self.options)
        
    def empty(self, findme_id):
        """Remove all phone numbers from a findme
            
        keyword arguments:
        findme_id -- ID of the findme to clear numbers
        
        """
        self.options['findme_id'] = findme_id
        self.options['action'] = 'findme.empty'
        return self.call(self.options)
    
    def get_findme_list(self):
        """ Get a list of all findme applications
        """
        self.options['action'] = 'findme.get_findme_list'
        return self.call(self.options)
    
    def get_phone_list(self, findme_id):
        """Get a list of all numbers in a findme
        
        keyword arguments:
        findme_id -- ID of findme containing numbers
        
        """
        self.options['findme_id'] = findme_id
        self.options['action'] = 'findme.get_phone_list'
        return self.call(self.options)
        
    def get_recorded_calls_list(self, findme_id):
        """ Get a list of recorded calls from a specific findme
        
        keyword argument:
        findme_id -- ID of findme associated with the recordings
        
        """
        self.options['findme_id'] = findme_id
        self.options['action'] = 'findme.get_recorded_calls_list'
        return self.call(self.options)
    
    def update_list_settings(self, **kwargs):
        """Update existing findme settings
        
        keyword arguments:
        name              -- name of the findme
        list_type         -- type of findme | 1: individual, 
                             2: customer service huntgroup
        loop_count        -- number of times to loop findme list 
        distribution_type -- How calls reach list. Values: 1, randomize; 2, 
                             round robin. Default: traverse list sequentially
        record            -- record calls
        screen_method     -- Screen caller for information before attempting to connect caller. 
                             Values: 0=Record callers name (default), 1=Use value in whisper_phrase 
                             as TTS, 2=Use value in whisper_audio. The whisper_audio value must 
                             be a file name for an existing whisper message in your account
        screen_prompt     -- TTS screening message
        dtmf_only         -- Requires person answering to use keypad to accept call. 
                             Values: 1, DTMF Only; 0, speech and DTMF 
        holdmusic         -- Audio file to play to caller as caller waits for destination to answer. 
                             Audio file must be in the account "holdme" directory. 
                             Default: Our standard audio file
        holdrepeat        -- How often the hold message is played to the caller. Values: 0, 
                             only once per Find Me session; 1, only once between each attempt 
                             to connect to a destination; 2, repeat continuosly between each 
                             connection attempt: default
        timeout           -- Number of seconds to ring each destination before attempting 
                             next destination (or end action). Values: 10-60. Default is 30
        whisper_phrase    -- Phrase spoken to person who answers phone, used when 
                             call screening is not enabled. Default: no phrase
        findme_action     -- Action to take if Find Me reaches end of list
        findme_action_parameter -- Building Block ID if required by End of List Action
        
        """
        self.options.update(kwargs)
        self.options['action'] = 'findme.update_list_settings'
        return self.call(self.options)