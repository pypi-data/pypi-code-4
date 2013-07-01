from base import IfbyphoneApiBase

class Locator(IfbyphoneApiBase):

    def add_location(self, **kwargs):
        """Add a store location
        
        keword arguments:
        usr_locator_id            -- ID of store locator
        location_destination      -- JSON encoded string | {"cmd":"XXXXX","parameter":"YYYYY"}
        location_zipcode          -- 5 digit zipcode
        location_name             -- name of the location | default: New Location
        location_address          -- address of the location
        location_desctipion       -- description of the location
        location_city             -- city of the location
        location_state            -- state of the location
        location_email_address    -- email address associated with location
        location_action_parameter -- location_destination | SON-encoded string with 
                                     the following format: {"cmd":"XXXXX","parameter":"YYYYY"} 
                                     where XXXXX is a supported command or "hangup1" through "hangup4"
        location_call_timeout     -- time to try calling a location | default: 40
        geocode_method            -- method for geocoding | default: yahoo API
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'locator.location.add'
        return self.call(self.options)
    
    def location_details(self, **kwargs):
        """Get details of a location in a store locator
        
        keyword arguments:
        usr_locator_id  -- ID of the store locator
        usr_location_id -- ID of the location
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'locator.location.details'
        return self.call(self.options)
        
    def list_locations(self, _id):
        """List all locations in a store locator
        
        keyword argument:
        _id -- ID of the store locator
        
        """
        
        self.options['usr_locator_id'] = _id
        self.options['action'] = 'locator.location.list'
        return self.call(self.options)
        
    def remove_location(self, **kwargs):
        """Remove a location from a store locator
        
        keyword arguments:
        usr_locator_id  -- ID of the store locator
        usr_location_id -- ID of the location to be removed
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'locator.location.remove'
        return self.call(self.options)
        
    def update_location(self, **kwargs):
        """Update configuration of a location
        
        keyword arguments:
        
        usr_locator_id            -- ID of the store locator
        usr_location_id           -- ID of the location to be updated
        location_destination      -- JSON encoded string | {"cmd":"XXXXX","parameter":"YYYYY"}
        location_zipcode          -- 5 digit zipcode
        location_name             -- name of the location | default: New Location
        location_address          -- address of the location
        location_desctipion       -- description of the location
        location_city             -- city of the location
        location_state            -- state of the location
        location_email_address    -- email address associated with location
        location_action_parameter -- location_destination | SON-encoded string with 
                                     the following format: {"cmd":"XXXXX","parameter":"YYYYY"} 
                                     where XXXXX is a supported command or "hangup1" through "hangup4"
        location_call_timeout     -- time to try calling a location | default: 40
        geocode_method            -- method for geocoding | default: yahoo API
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'locator.location.update'
        return self.call(self.options)