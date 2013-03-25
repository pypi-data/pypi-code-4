##########################################################################
#This file is part of WTFramework. 
#
#    WTFramework is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    WTFramework is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with WTFramework.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################
from wtframework.wtf.config import WTF_CONFIG_READER

"""
The purpose of this class is to provide tools for helping debug WTF tests.
"""
from datetime import datetime
import inspect

class TimeDebugger(object):
    "Object to keeps track of time and has utility methods to print it"
    

    def start_timer(self):
        self.start_time = datetime.now()

    def print_time(self, message="Time is now: ", print_frame_info=True):
        if print_frame_info:
            frame_info = inspect.getouterframes(inspect.currentframe())[1]
            print message, (datetime.now() - self.start_time), frame_info
        else:
            print message, (datetime.now() - self.start_time)
        
    def get_split(self):
        return (datetime.now() - self.start_time)


def print_debug(*args):
    if WTF_CONFIG_READER.get("debug", False) == True:
        print args