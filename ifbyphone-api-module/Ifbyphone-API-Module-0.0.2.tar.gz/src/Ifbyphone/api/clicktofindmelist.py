from base import IfbyphoneApiBase

class Clicktofindmelist(IfbyphoneApiBase):

    def _call(self, **kwargs):
        """Initiate a call to a phone number and try to 
           connect that call to specified list of phone numbers
           
        keyword arguments:
        list            -- list of numbers to connect caller to
        phone_to_call   -- number to call 
        screen_prompt   -- message to play to caller 
        type            -- '1': regular findme '2': reverse findme   
        usr_findme_type -- '1': Individual Find Me (default) 
                           '2' :Customer Service Hunt Group
        loop_count      -- number of times to loop findme list 
        randomize       -- bool | specify if number list should be randomized
        record          -- record calls
        use_screen      -- option to screen caller for information
        dtmf_only       -- Requires person answering to use keypad to accept call. 
                           Values: 1, DTMF Only; 0, speech and DTMF 
        holdmusic       -- Audio file to play to caller as caller waits for destination to answer. 
                           Audio file must be in the account "holdme" directory. 
                           Default: Our standard audio file
        holdrepeat      -- How often the hold message is played to the caller. Values: 0, 
                           only once per Find Me session; 1, only once between each attempt 
                           to connect to a destination; 2, repeat continuosly between each 
                           connection attempt: default
        timeout         -- Number of seconds to ring each destination before attempting 
                           next destination (or end action). Values: 10-60. Default is 30
        whisper_phrase  -- Phrase spoken to person who answers phone, used when 
                           call screening is not enabled. Default: no phrase
        nextaction      -- Action to take if Find Me reaches end of list
        nextactionitem  -- Building Block ID if required by End of List Action
        no_answer_email -- address to send an email if no answer
        no_answer_sms   -- number to send an SMS if no answer
        no_answer_url   -- URL to send xml data if no answer
        no_answer_phone -- phone number to transfer call if no answer

        """
        
        self.options.updaet(kwargs)
        self.options['app'] = 'ctfl'
        return self.call(self.options, 'click_to_xyz.php', 'key')