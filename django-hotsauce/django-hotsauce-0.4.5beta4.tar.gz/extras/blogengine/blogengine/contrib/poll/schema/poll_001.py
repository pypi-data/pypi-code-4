# Copyright (C) 2007-2013 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
#
# Please see the "LICENSE" file included in the BlogEngine source 
# distribution for details on licensing info.

import base64
import datetime

from schevo.schema import *
from schevo.constant import UNASSIGNED
schevo.schema.prep(locals())

# XXX django compat <= 1.3
from notmm.utils.decorators import permalink
from notmm.utils.markup import convert2markdown

__all__ = ['Vote', 'Poll']

class Vote(E.Entity):
    # yes,no,whatever,blah
    title = f.string(required=True)
    related_poll = f.entity('Poll')
    # this vote was selected n times by n persons
    count = f.integer(default=0)

    def get_vote_count(self):
        pass

class Poll(E.Entity):
    """A minimal micro message model"""
    
    # class Poll (do you like methylphenidate in your cereals?)
    # choice a
    # choice b
    # choice c
    author = f.entity('accounts.Author') #f.entity('User', dbname='accounts')
    title = f.string(required=True, multiline=True)
    pub_date = f.datetime(default=datetime.datetime.today)
    
    def __str__(self):
        return "<Poll: %s>" % self.title

    class Meta:
        pass

    #_key(sender_name, blogentry)
    #_key(blogentry)

