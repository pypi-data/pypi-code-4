from base import IfbyphoneApiBase

class Routing(IfbyphoneApiBase):

    def advanced(self, **kwargs):
        """Configure advanced routing options for a number
        
        keyword arguments:
        phone_number -- the phone number to configure
        reverse_lookup -- set to 1 to perform reverse lookup 
        record_call    -- values are 0 for no recording 
                          1 for 'Record after transfer 
                          2 for 'Record whole call'
                          3 for 'Record up to transfer'
        record_warning -- values are 0 for both caller and recipient 
                          1 for the caller
                          2 for the recipient
                          3 for none.
        caller_audio   -- filename saved in your Call Recording Warning 
                          Audio directory to play for the caller
        recipient_audio -- filename saved in your Call Recording Warning 
                           Audio directory to play for the recipient
        always_ring    -- values are 0 for off and 1 for on. The default is 0
        ga_referrer    -- provide a value for Google Analytics referrer
        ga_content     -- provide a value for Content for Google Analytics
        ga_campaign    -- provide a value for a Campaing name for Google Analytics
        ga_term        -- provide a value for a keyword associated 
                          with your number for Google Analytics
        ga_medium      -- provide a value for a medium associated with your number
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'routing.advanced'
        return self.call(self.options)
        
    def configure(self, **kwargs):
        """Configure standard routing for a phone number
        
        keword arguments:
        phone_number -- the phone number to configure
        routing_type -- valid types: findme, transfer, 
                        transfer_w_whisper, survo, locator, 
                        broadcast_from_phone, call_distributor, 
                        phone_directory, vmail
        parameter1   -- parameter for the selected routing type:
        parameter2
        parameter3
        parameter4
                        findme: 1 - Building Block ID of Find Me (required)
                                2 - Prompt to read to caller using TTS (optional)
                                3 - Whisper phrase (optional)
                        transfer_w_whisper:
                                1 - Transfer To Number (required)
                                2 - Prompt to read to caller using TTS (optional)
                                3 - Whisper Phrase spoken using TTS (optional)
                                4 - Record Call (optional)
                        survo:
                                1 - Building Block ID of SurVo (required)
                                2 - Prompt to read to caller using TTS (optional)
                        transfer:
                                1 - Phone number to transfer to (required)
                                2 - Prompt to read to caller using TTS (optional)
                        locator:
                                1 - Building Block ID of Store Locator (required)
                        voting:
                                1 - Building Block ID of Polling Event (required)
                        vmail:
                                1 - Building Block ID of Voice Mail Box (required)
                                2 - Prompt to read to caller using TTS (optional)
                        broadcast_from_phone:
                                1 - Group ID (required). Use 0 to select group from phone
                        phone_directory:
                                1 - Building Block ID of the Phone Directory (required)
                        virtual_receptionist
                                1 - Building Block ID of the Virtual Receptionist (required)
        description  -- set phone label description
        record_call  -- turn call recording on | 1 for on, 0 for off
        recording_wargind -- determine which call party recieves call record warning:
                             0 - Both caller and recipient (default)
                             1 - Caller only
                             2 - Recipient only
                             3 - None
        reverse_lookup -- perform reverse lookup on all calls
        playe_ring     -- recommended for whole call recording
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'routing.configure'
        return self.call(self.options)
        
    def numbers(self, format):
        """Retrieve a list of numbers in your account
        
        keyword argument:
        format -- 'csv' 'xml'
        
        """
        
        self.options['format'] = format
        self.options['action'] = 'routing.numbers'
        return self.call(self.options)
        
    def update_lable(self, **kwargs):
        """Update a phone number label for a single label
        
        keyword arguments:
        phone_number -- the phone number to update
        description  -- the new phone label
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'routing.update_label'
        return self.call(self.options)