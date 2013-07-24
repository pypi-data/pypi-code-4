from base import IfbyphoneApiBase

class Report(IfbyphoneApiBase):

    def broadcast(self, **kwargs):
        """ Get a report of broadcasts within a time range
        
        keyword arguments:
        start_date   -- start date for the report in YYYYMMDD
        end_date     -- end date for the report in YYYYMMDD
        broadcast_id -- (optional) unique ID of broadcast
        type         -- type of broadcast | 'survo' 'basic' or 'all'
        format       -- xml, csv, or text
        number       -- filter to show results for a given number
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'report.broadcast'
        return self.call(self.options)
        
    def call_detail(self, **kwargs):
        """Retrieve call detail results
        
        keyword arguments:
        start_date   -- start date for the report in YYYYMMDD
        end_date     -- end date for the report in YYYYMMDD 
        format       -- xml, csv, or text
        start_time   -- Daily start time. Must be used with 
                        end_time to create a daily time range
        end_time     -- Daily start time. Must be used with 
                        end_time to create a daily time range
        date_added   -- date/time the call was made
        call_type_filter -- 'inbound' 'outbound' 'click-To'
        phone_label  -- the label assigned to the number
        dnis         -- number dialed
        ani          -- caller ID
        first_activity -- first action taken on the call 
        last_activity  -- last action taken on the call 
        activity_info  -- all activities on the call 
        click_description -- if type 'click-To this will display
                             the description assigned to the click-To
        switch_minutes    -- duration, in tenths of a minute, a call 
                             is on the system while not connected to a 2nd leg
        network_minutes   -- duration, in tenths of a minute, that two parties
                             are connected together
        enhanced_minutes  -- duration, in tenths of a minute, when a caller 
                             is being recorded
        adj_switch        -- switch minutes rounded up to the next minute
        adj_network       -- network minutes rounded up to the next minute
        adj_enhanced      -- enhanced minutes rounded up to the next minute
        call_duration     -- total duration rounded up to the next minute
        transfer_type     -- application that transfered call 
        transfer_to_number -- number caller was transfered to
        last_name         -- last name of the caller if reverse lookup was enabled
        first_name        -- first name of the caller if reverse lookup was enabled
        street_address    -- street address of the caller if reverse lookup was enabled
        city              -- city of the caller if reverse lookup was enabled
        state             -- state of the caller if reverse lookup was enabled
        zipcode           -- zip code of the caller if reverse lookup was enabled
        call_type_value   -- filter by call type 
        call_type         -- display call type column 
        sid               -- display session ID
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'report.call_detail'
        return self.call(self.options)
        
    def call_detail_csv(self, **kwargs):
        """Return call detail report information in csv format
        
        keyword arguments:
        start_date   -- start date for the report in YYYYMMDD
        end_date     -- end date for the report in YYYYMMDD
        lookup       -- set to 1 to include reverse lookup data
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'report.call_detail_csv'
        return self.call(self.options)
        
    def clickto(self, **kwargs):
        """Retrieve results for all click-to calls
        
        keword arguments:
        start_date   -- start date for the report in YYYYMMDD
        end_date     -- end date for the report in YYYYMMDD
        click_id     -- ID of a specific click to call | default is all
        ref          -- optional value within 'ref' field
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'report.clickto'
        return self.call(self.options)
        
    def survo(self, **kwargs):
        """Get results for a specific SurVo (IVR)
        
        keyword arguments:
        start_date   -- start date for the report in YYYYMMDD
        end_date     -- end date for the report in YYYYMMDD
        id           -- SurVo ID to get results from
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'report.survo'
        return self.call(self.options)