from base import IfbyphoneApiBase

class Clicktosurvo(IfbyphoneApiBase):
    
    def _call(self, **kwargs):
        """Connect a recipient to an IVR application
        
        keyword arguments:
        survo_id       -- ID of the IVR to use 
        usr_parameters -- 
        p_t            -- any valid string 
        phone_to_call  -- phone number to call 
        schedule_only  -- bool | used for scheduled calls 
        first_callerid -- caller ID to show the recipient

        scheduled call parameters (used with schedule_only):
        
        phone -- The phone number(s) scheduled to receive the SurVo Broadcast call. 
                 May be a single phone number, a "|" delimited list of phone numbers, 
                 or a fully qualified URL to a web-accessible and valid CSV file
                 If you use phone do not use phone_to_call
        sdate    -- broadcast starting time | format: YYYY-MM-DD HH:MM
        edate    -- broadcast ending   time | format: YYYY-MM-DD HH:MM
        dstime   -- daily call range starting time | format: HH:MM
        detime   -- daily call range ending time   | format: HH:MM
        tz       -- timezone date/time values | values: 'Eastern', 'Central', 
                    'Mountain', 'Pacific', 'Alaska', 'Hawaii' default is 'Eastern'
        type     -- '1': spread all calls evenly '2': send calls as fast as possible
        attempts -- maximum number of retry attempts for each phone number
        retry    -- number of minutes between retry attempts on a phone number
                    valid values: 5,10,15,30,60,90,120 default is 5
        simul    -- number of simultaneous calls | valid values: 1,2,3
        cid      -- caller ID to show recipients
        desc     -- description of the scheduled broadcast 
        
        """
        
        self.options.update(kwargs)
        self.options['app'] = 'cst'
        return self.call(self.options, 'click_to_xyz.php', 'key')