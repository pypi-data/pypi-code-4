from base import IfbyphoneApiBase

class Broadcast(IfbyphoneApiBase):

    def create(self, **kwargs):
        """ Create a voice broadcast to be scheduled
        
        keyword arguments:
        name                   -- name for broadcast
        recording_phone_number -- number to dial to record audio message
        phone                  -- required if schedule param is set. url, 
                                  csv file, or bar delimited number ListType
        machine_detection      -- set to 1 to record a specific message for 
                                  answering machines
        use_transfer           -- set to 1 to transfer during a broadcast
        transfer_number        -- number where calls will be transfered to
        schedule               -- set to 1 to schedule the broadcast
        simul                  -- number of calls to make every 2 minutes. 
                                  max typically 25
        timestamp              -- specify timestamp for start of broadcast
        dstime                 -- specify start time | HH:ii
        detime                 -- specify end time   | HH:ii
        recording_cid          -- set caller ID for number receiving call to record
        desc                   -- description of the broadcast
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'broadcast.create'
        return self.call(self.options)
        
    def get_optout(self, **kwargs):
        """ Get a list of phone numbers of people that have opted out from broadcasts.
        
        keyword arguments:
        active       -- display only active broadcasts
        broadcast_id -- get optouts for a specific broadcast
        created_date -- get optouts within a date range | YYY-MM-DD
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'broadcast.get_optout'
        return self.call(self.options)
        
    def history(self):
        """ Get a list of all future and completed broadcasts
        """
        self.options['action'] = 'broadcast.history'
        return self.call(self.options)
        
    def optout(self, number):
        """ Add a phone number to the opt out ListType
        
        keyword arguments:
        phone_number -- 10digit number to add to optout list
        """
        self.options['phone_number'] = number
        self.options['action'] = 'broadcast.optout'
        return self.call(self.options)
    
    def schedule(self, **kwargs):
        """ Schedule a created broadcast
        
        keyword arguments:
        phone_number_list -- bar delimited, url, or csv of numbers
        audio_dialog_id   -- ID of the audio dialog to play as message
        timestamp         -- date/time for calls to begin | YYYY-MM-DD HH:ii
        edate             -- end date | (required if type set to 1)
        type              -- set to 1 to spread calls evenly. set to 2 to send calls immediately
        attempts          -- number of times to call if number is busy or no answer | max = 3
        retry             -- number of minutes between retries | 
                             valid values: 5, 10, 15, 20, 25, 30, 60, 90, 120
        cid               -- caller ID displayed to broadcast recipients
        dstime            -- start time | HH:ii
        detime            -- end time   | HH:ii
        simul             -- number of calls to make every two minutes | max typically 25
        desc              -- description | used for management in gui                     
        
        """
        self.options.update(kwargs)
        self.options['action'] = 'broadcast.schedule'
        return self.call(self.options)
        
    def status(self, _id, gmt):
        """ Get the status of calls made during a broadcast
        
        keyword arguments:
        _id -- ID of the broadcast to get status of
        gmt -- timezone to convert times to | default: eastern
        
        """
        self.options['gmt'] = gmt
        self.options['basic_broadcast_id'] = _id
        self.options['action'] = 'broadcast.status'
        return self.call(self.options)
        
    def stop(self, _id):
        """ Stop a broadcast, effectively deleting it
        
        keyword argument:
        _id -- ID of the broadcast to stop 
        
        """
        self.options['basic_broadcast_id'] = _id
        self.options['action'] = 'broadcast.stop'
        return self.call(self.options)