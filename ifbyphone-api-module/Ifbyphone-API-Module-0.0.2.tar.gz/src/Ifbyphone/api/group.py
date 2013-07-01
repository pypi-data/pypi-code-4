from base import IfbyphoneApiBase

class Group(IfbyphoneApiBase):

    def create(self, name):
        """Create a new group
        
        keyword argument:
        name -- name of the group
        
        """
        self.options['group_name'] = name 
        self.options['action'] = 'group.create'
        return self.call(self.options)
    
    def details(self, _id):
        """ List names, phone numbers, and emails of contacts in a group
        
        keyword argument:
        _id -- group ID
        
        """
        
        self.options['group_id'] = _id
        self.options['action'] = 'group.details'
        return self.call(self.options)
        
    def empty(self, _id):
        """ Remove contacts from a group
        
        keyword argument:
        _id -- ID of the group to remove contents
        
        """
        
        self.options['group_id'] = _id
        self.options['action'] = 'group.empty'
        return self.call(self.options)
        
    def list(self):
        """ List all groups
        """
        
        self.options['action'] = 'group.list'
        return self.call(self.options)
        
    def member_add(self, **kwargs):
        """Add a member to a contact group
        
        keyword arguments:
        group_id     -- ID for the group contact is added to
        member_name  -- name of the new member
        member_phone -- phone number of the new member
        members      -- bar delimited list of members to add
        member_email -- email address of the new member
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'group.memberadd'
        return self.call(self.options)
        
    def member_remove(self, _id):
        """Remove a member from a group
        
        keyword argument:
        _id -- ID of the member to remove
        
        """
        
        self.options['member_id'] = _id
        self.options['action'] = 'group.memberremove'
        return self.call(self.options)
        
    def remove(self, _id):
        """Remove an existing group
        
        keyword argument:
        _id -- ID of the group to remove
        
        """
        
        self.options['group_id'] = _id
        self.options['action'] = 'group.remove'
        return self.call(self.options)
        
    def rename(self, **kwargs):
        """Rename an existing group
        
        keyword arguments:
        group_id -- ID of the group to rename
        name     -- new name of the group
        
        """
        
        self.options.update(kwargs)
        self.options['action'] = 'group.rename'
        return self.call(self.options)