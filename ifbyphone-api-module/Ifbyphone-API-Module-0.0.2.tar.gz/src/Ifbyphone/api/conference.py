from base import IfbyphoneApiBase

class Conference(IfbyphoneApiBase):

    def attendee_add(self, **kwargs):
        """ Add one or more attendees to existing smart conference
        
        keyword arguments:
        usr_conference_id -- ID for conference where attendee(s) will be added
        attendee_list     -- A double bar-delimited list of bar-delimited attendees 
                             in these formats: 1112223333|Attendee Name|x@x.com 
                             or 2223334444|Attendee Name, or a CSV file that is no more than 512KB 
                             with required "attendee_name" and "phone_number" columns plus optional 
                             "email_address" column. Possibilities for CSV can come from either 
                             an HTTP POST upload, or a fully-qualified HTTP(S)/FTP(S) URL.
        invitations       -- If specified (value is irrelevant), all conference attendees with 
                             valid e-mail addresses will receive an e-mail invitation containing 
                             information about their participation
        immediate         -- If specified (value is irrelevant), the newly added conference 
                             attendees will be called immediately.
        """
        self.options.update(kwargs)
        self.options['action'] = 'conference.attendee.add'
        return self.call(self.options)
        
    def call(self, **kwargs):
        """ Call an attendee and add them to ongoing conference
        
        keyword arguments:
        usr_conference_id               -- ID for conference where attendee will be added
        usr_conference_attendee_id      -- ID of conference attendee to call
        usr_conference_participation_id -- If specified, this value is found in the <usr_conference_participation_id> 
                                           field within a given <participation> block of conference attendees provided 
                                           by API calls to conference.attendee.list or conference.attendee.details, 
                                           and is mainly used if the attendee participated with a different phone number 
                                           than expected. If not specified, the conference attendee's 
                                           assigned phone number will be called
        """
        self.options.update(kwargs)
        self.options['action'] = 'conference.attendee.call'
        return self.call(self.options)
        
    def details(self, conf_id, attendee_id):
        """ Get the details of an attendee's participation on a call
        
        keyword arguments:
        conf_id     -- conference ID the conference attendee ID belongs to
        attendee_id -- conference ID to list details for
        """
        self.options['usr_conference_id'] = conf_id
        self.options['usr_conference_attendee_id'] = attendee_id
        return self.call(self.options)
        
    def kick(self, conf_id, number):
        """ Kick a user from from a conference call 
        
        keyword arguments:
        conf_id -- conference ID to kick the attendee from
        number  -- This value is found in the <user_number> field 
                   within a given <participation> block of conference 
                   attendees provided by API calls to 'conference.attendee.list' 
                   or 'conference.attendee.details', and indicates the active 
                   participation identifier on the conference.
        """
        self.options['user_number'] = number
        self.options['usr_conference_id'] = conf_id
        return self.call(self.options)
        
    def list_attendees(self, conf_id):
        """ Get a list of attendees scheduled for a conference
        
        keyword argument:
        conf_id -- Conference ID to list conference attendees for
        
        """
        self.options['usr_conference_id'] == conf_id
        self.options['action'] = 'conference.attendee.list'
        return self.call(self.options)
    
    def mute(self, conf_id, number):
        """ Mute a conference participant
        
        keyword arguments:
        conf_id -- conference ID the conference participant to mute belongs to
        number  -- the user_number may be found by using the attendee.list or 
                   attendee.details web requests. The response for each attendee 
                   includes a participation element, which has a user_number 
                   element if the attendee is currently on a call
        """
        self.options['user_number'] = number
        self.options['usr_conference_id'] = conf_id
        return self.call(self.options)
        
    def remove_attendee(self, conf_id, attendee_id):
        """ Remove an attendee from a conference
        
        keyword arguments:
        usr_conference_id          -- conference ID to remove attendee(s) from
        usr_conference_attendee_id -- either a single conference attendee ID, 
                                      or a bar-delimited list of conference attendee 
                                      IDs to remove from the conference. Will only succeed 
                                      for conference attendees that have not yet actively 
                                      participated in the conference
        """
        self.options['usr_conference_id'] = conf_id
        self.options['usr_conference_attendee_id'] = attendee_id
        self.options['actions'] = 'conference.attendee.remove'
        return self.call(self.options)
        
    def unmute(self, conf_id, number):
        """Un-mute a muted conference participant
        
        keyword arguments:
        conf_id -- conference ID the conference participant to unmute belongs to
        number  -- this value is found in the <user_number> field within a given 
                   <participation> block of conference attendees provided by API 
                   calls to 'conference.attendee.list' or 'conference.attendee.details'
                   and indicates the active participation identifier on the conference
        """
        self.options['user_number'] = number
        self.options['usr_conference_id'] = conf_id
        self.options['action'] = 'conference.attendee.unmute'
        return self.call(self.options)
        
    def details(self, conf_id):
        """ Get the details of a specific conference
        
        keyword argument:
        conf_id -- ID of the conference to get details from
        
        """
        self.options['usr_conference_id'] = conf_id
        self.options['action'] = 'conference.schedule'
        return self.call(self.options)
        
    def list_conferences(self):
        """ List all scheduled and completed conferences
        """
        self.options['action'] = 'conference.list'
        return self.call(self.options)
        
    def remove_conference(self,  conf_id):
        """ Remove a conference that is not active
        
        keyword argument:
        conf_id -- ID of conference to remove
        
        """
        self.options['usr_conferenc_id'] = conf_id
        self.options['actions'] = 'conference.remove' 
        return self.call(self.options)
    
    def schedule(self, **kwargs):
        """ Schedule a conference call 
        
        keyword arguments:
        attendee_list -- a double bar-delimited list of bar-delimited attendees 
                         in these formats: 1112223333|Attendee Name|x@x.com OR 
                         2223334444|Attendee Name, or a CSV file that is no more 
                         than 512KB with required "attendee_name" and "phone_number" 
                         columns plus optional "email_address" column. Possibilities 
                         for CSV can come from either an HTTP POST upload, or a 
                         fully-qualified HTTP(S)/FTP(S) URL
        scheduled_time -- the scheduled start time for the conference (YYYY-MM-DD HH:MM ZZZZ), 
                          in 24-hour time with optional GMT offset (defaults to -0500) for proper 
                          time zone handling. Time will be rounded up to the nearest 5th minute. 
                          If not specified, or the scheduled time fails to match the above format exactly, 
                          the conference will execute immediately and begin calling each attendee
        conference_length -- Length of the conference, in minutes, between 10 and 240, rounded, 
                             which will be up to the near 5th minute. If not specified, the default 
                             conference length is 30 minutes
        conference_name -- name of the conference | (displayed in gui)
        pin             -- 4 digit pin for delegating access to a conference
        inboundonly     -- If specified (value is irrelevant), the conference will be available 
                           for inbound calls beginning 5 minutes before its scheduled time, but 
                           attendees will not be called at the scheduled time
        invitations     -- If specified (value is irrelevant), all conference attendees with valid 
                           e-mail addresses will receive an e-mail invitation containing information 
                           about their participation
        desc            -- description of the conference
        
        """
        self.options.update(kwargs)
        self.options['action'] = 'conference.schedule'
        return self.call(self.options)
    