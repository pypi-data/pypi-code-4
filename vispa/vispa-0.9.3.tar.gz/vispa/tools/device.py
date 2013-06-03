# -*- coding: utf-8 -*-

# Imports
import cherrypy
from os.path import join
import vispa
from vispa.helpers import browser

__all__ = ['DeviceTool']

class DeviceTool(cherrypy.Tool):

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler', self._fetch, priority=56)

    def _fetch(self, devices=None, groups=None, url="", reverse=False):
        """ There is a priority order: devices => groups!
            Both devices and groups can be strings or lists of strings.
        """
        
        wrongdevice = True
        agent = browser.client_agent()
        session_agent = browser.get_session_value("d_agent")
        if session_agent != agent:
            browser.set_session_value("d_name")
            browser.set_session_value("d_group")
        session_device = browser.get_session_value("d_name")
        session_group = browser.get_session_value("d_group")
        
        # try to match with priority order as given above
        if devices is not None:
            if not isinstance(devices, list):
                devices = [devices]
            for device in devices:
                if device != session_device:
                    success, matched_device = self.devicematch(agent, device)
                    if success:
                        browser.set_session_value("d_name", matched_device)
                        wrongdevice = False
                        break
                else:
                    wrongdevice = False
        elif groups is not None:
            if not isinstance(groups, list):
                groups = [groups]
            for group in groups:
                if group != session_group:
                    success, matched_group, matched_device = self.groupmatch(agent, group)
                    if success:
                        browser.set_session_value("d_group", matched_group)
                        browser.set_session_value("d_name", matched_device)
                        wrongdevice = False
                        break
                else:
                    wrongdevice = False
        
        # set the d_agent to the session for the next time
        browser.set_session_value("d_agent", agent)
        
        # redirect?
        if (wrongdevice and not reverse) or (not wrongdevice and reverse):
            raise cherrypy.HTTPRedirect(join(vispa.url.base_static, url))

    def groupmatch(self, agent, group="all"):
        group = group.lower()
        # default case?
        if group == "all":
            return True, group, None
        
        # group known?
        if group not in DEVICE_GROUPS.keys():
            raise KeyError("Group '%s' not known" % group)
        
        # a single match in all devices
        # of the group is sufficient
        for device in DEVICE_GROUPS[group]:
            success, matched_device = self.devicematch(agent, device)
            if success:
                return True, group, matched_device
        
        # no match in this group
        return False, None, None


    def devicematch(self, agent, device="all"):
        agent = agent.lower()
        device = device.lower()
        
        # default case?
        if device == "all":
            return True, device
        
        # device known?
        device_obj = None
        known = False
        for key in DEVICES.keys():
            if device == key:
                device_obj = DEVICES[key]
                known = True
        if not known:
            raise KeyError("Device '%s' not known" % device)
        
        # exceptions
        # ---------------------------------------
        exceptions = device_obj.exceptions
        
        # string to list
        if not isinstance(exceptions, list):
            exceptions = [exceptions]
        
        # loop
        for exception in exceptions:
            # list in list?
            if isinstance(exception, list):
                hits = 0
                for elem in exception:
                    if agent.find(elem) != -1:
                        hits += 1
                if len(exception) == hits:
                    return False, None
            else:
                if agent.find(exception) != -1:
                    return False, None
        
        # matches
        # ---------------------------------------
        matches = device_obj.matches
        
        # string to list
        if not isinstance(matches, list):
            matches = [matches]
        
        # loop
        for match in matches:
            # list in list?
            if isinstance(match, list):
                hits = 0
                for elem in match:
                    if agent.find(elem) != -1:
                        hits += 1
                if len(match) == hits:
                    return True, device
            else:
                if agent.find(match) != -1:
                    return True, device
        
        # no match
        return False, None

    def get_device_name(self, agent):
        device_name = ""
        for device in DEVICES.keys():
            success, name = self.devicematch(agent, device)
            if success:
                device_name = name
                break
        return device_name


class Device:

    name = None
    matches = None
    exceptions = None

    def __init__(self, name, matches=None, exceptions=None):
        # set the parameters
        self.name = name
        self.exceptions = exceptions or []
        self.matches = matches or [name]


""" MATCH ALGORITHM:
    A device is defined by up to three parameters: name, matches and exceptions.
        1. "name" is just a representative string to describe the device
        2. "matches" define substrings that should match the user agent in order
           to associate the user agent with that device. The type should be a list.
           A passed string is converted to a list with length 1. If one of the elements
           of that list can be matched, the device match succeeds. To create more precise
           matches, the "matches" list can contain lists itself. If one of the elements of
           "matches" is a list, all of its elements have to match the user agent!
        3. "exceptions" is the opposite of "matches". Again, it can by a string (that will be
           converted to a list) or a list, that may contain strings or lists. If one of the
           elements of "exceptions" is found, the device match will return False. If one
           element is a list itself, all of its elements have to be found.
"""

# set known devices
DEVICES = {"iphone":              Device("iphone"),
           "ipod":                Device("ipod"),
           "ipad":                Device("ipad"),
           "macintosh":           Device("macintosh"),
           "blackberry":          Device("blackberry"),
           "blackberry_playbook": Device("blackberry_playbook", matches=[["playbook", "rim", "tablet"]]),
           "nokia_n9":            Device("nokia_n9", matches="nokian9"),
           "nexus":               Device("nexus"),
           "windows":             Device("windows", matches=["windows", "compatible"])}

# please update
DEVICE_GROUPS = {"mobile": ["iphone", "ipod", "blackberry", "nokia_n9", "nexus"],
                 "tablet": ["ipad", "blackberry_playbook"],
                 "pc":     ["macintosh", "windows"]}