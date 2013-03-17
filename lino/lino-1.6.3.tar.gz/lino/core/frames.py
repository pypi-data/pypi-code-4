## Copyright 2009-2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.
"""
Defines classes :class:`Frame` and :class:`FrameHandle`
"""

import logging
logger = logging.getLogger(__name__)

from lino.ui import base
from lino.core import actors
from lino.core import actions

class FrameHandle(base.Handle): 
    """
    Deserves more documentation.
    """
    def __init__(self,ui,frame):
        #~ assert issubclass(frame,Frame)
        self.actor = frame
        base.Handle.__init__(self,ui)

    def get_actions(self,*args,**kw):
        return self.actor.get_actions(*args,**kw)
        
    def __str__(self):
        return "%s on %s" %(self.__class__.__name__,self.actor)



class Frame(actors.Actor): 
    """
    Deserves more documentation.
    """
    _handle_class = FrameHandle
    #~ default_action_class = None
    editable = False
    
    #~ @classmethod
    #~ def class_init(self):
        #~ self.default_action = self.get_default_action()
        #~ super(Frame,self).class_init()
        
    @classmethod
    def do_setup(self):
        #~ logger.info("%s.__init__()",self.__class__)
        #~ if not self.__class__ is Frame:
        #~ if self.default_action_class:
            #~ self.default_action = self.default_action_class(self)
        #~ self.default_action = self.get_default_action()
        if not self.label:
            self.label = self.default_action.action.label
            #~ self.default_action.actor = self
        super(Frame,self).do_setup()
        #~ self.set_actions([])
        #~ self.setup_actions()
        #~ if self.default_action:
            #~ self.add_action(self.default_action)


