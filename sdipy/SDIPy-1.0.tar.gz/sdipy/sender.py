"""
sender.py

by Charles Fracchia, Copyright (c) 2013

Sender class module

This class defines data and methods for the sender in a packet
"""
import re, warnings

allowedAttributes = ["name","brand","model","modelNum"]       #In future, this could be loaded dynamically from a reference JSON

class Sender(object):
  """docstring for Packet"""
  
  def __init__(self, address, timeFormat, startTime="", **kwargs):
    super(Sender, self).__init__()
    if (self._validateAddress(address) != False) :         #Validate submitted address
      self.addressType = self._validateAddress(address)
      self.address = address
      
    if startTime != "":
      if self._validateTimeFormat(timeFormat,startTime):
        self.timeFormat = timeFormat
        self.startTime = startTime
      else:
        raise ValueError("The specified time format or start time in the sender object is incorrect.")
    else:                                                   #If a Start Time object was not passed
      if self._validateTimeFormat(timeFormat):
        self.timeFormat = timeFormat
      else:
        raise ValueError("The specified time format in the sender object is incorrect.")
      
    #For each extra attribute add it to the object to expose it
    for arg in kwargs:
      if arg not in allowedAttributes:                    #If it's not an allowed attribute according to SDIP
        allowedList = ""                                  #Used for nicely formatted warning
        for attribute in allowedAttributes:               #For each of the attributes in the list
          if allowedList != "": allowedList = allowedList + ", " + attribute    #Nicely formatted :)
          else: allowedList += attribute                  #Nicely formatted :)
        warnings.warn("Invalid sender attribute passed. Attribute will not be set. Allowed attributes are: %s" % allowedList)     #Warn the user
      else:
        setattr(self, arg, kwargs[arg])                   #This sets the attribute with dynamic name
  
  def __str__(self):
    return "*********************\nSDIP Sender Object\nAddress: %s (%s)\n*********************" % (self.address,self.addressType)
    
  def _validateAddress(self, address):
    """
    Check that the [address] is a valid address and return its type
    Return destination address if correct, Nothing otherwise. If it is a MAC address it will return it as a byte field (xAAxBBxCCxDDxEExFFxGGxHH)
    Acceptable: 
        XBee MAC address formatted like AA:BB:CC:DD:EE:FF:GG:HH:GG:HH
        IP address formatted like 000.000.255.255, each block has to be 0 <= n < 256
    """
    pass
    addressType = []                                    #Used for storing regex matches
    mac = '^[a-fA-F0-9][aceACE02468][:|\-]?([a-fA-F0-9]{2}[:|\-]?){4}[a-fA-F0-9]{2}$'                 #For regular mac addresses
    beemac = '^[a-fA-F0-9][aceACE02468][:|\-]?([a-fA-F0-9]{2}[:|\-]?){6}[a-fA-F0-9]{2}$'              #For XBee mac addresses
    ip = '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'  #For IP addresses
    
    regexes = {"mac":mac,"beemac":beemac,"ip":ip}
    
    for regex in regexes:
      regexFound = re.compile(regexes[regex]).search(address)    #Do the regex search
      if regexFound != None:                            #If it finds a match
        addressType.append("%s" % regex)                #append the type to an array, this way we can detect addresses that match multiple regexes
    
    if len(addressType) != 1:                           #If we matched too many regex
      raise ValueError("The provided address is not correctly formatted. The address can be an IP, regular MAC address or ZigBee MAC address")
      return False
    else:                                               #We correctly matched just 1 type
      return addressType[0]                             #Return the address type matched
  
  def _validateTimeFormat(self, timeformat, startTime=""):
    """
    This validates the time format
    Takes the timeformat as a string
    Returns True if the timeformat is valid, False if not
    """
    pass
    allowedTimeFormats = ["sec","microsec","millisec"]
    allowedTimeTypes = ["epoch","rel"]
    
    splitTime = timeformat.split("-")
    #print splitTime                                    #DEBUG
    if (splitTime[0] in allowedTimeFormats and splitTime[1] in allowedTimeTypes):       #Check that the timeformat is correctly formatted
      if splitTime[1] == "rel":                         #Time is relative, need to look at the start time
        if startTime != "":                             #StartTime was passed along so we're good
          if self._validateStartTime(startTime):        #Time to validate the StartTime object
            return True                                 #StartTime is good
          else:
            raise ValueError("You indicated a relative time format but the start time object is malformed")
            return False                                #StartTime is malformed
        else:                                           #StartTime was not passed along but time is relative grrr...
          raise KeyError("You indicated a relative time format but failed to pass a start time object")
          return False
          
      elif splitTime[1] == "epoch":                     #Time is absolute and uses unix epoch as reference
        if startTime != "":
          warnings.warn("You've passed a start time dictionnary but are using absolute timing (epoch in this case). Make sure you \
          understand the different types of time units we support, cause it looks like you don't :)",UserWarning)
        return True
      else:
        raise ValueError("Your time format string is unsupported. We currently only support relative (with start time) and epoch data timestamps")
        return False                                    #Currently no other formats supported
    else:
      raise ValueError("Your time format string is malformed")
      return False                                      #Malformed string

  def _validateStartTime(self, startTime):
    """
    Validates the startTime dictionnary
    Takes in a dictionnary of the following form: {"format": "sec-epoch", "time": 1383842840}
    Returns True if startTime is correctly formed or False if not
    """
    pass
    allowedTimeFormats = ["sec","microsec","millisec"]
    allowedTimeTypes = ["epoch","rel"]
    try:
      splitStartTime = startTime['format'].split("-")
      #print splitStartTime                            #DEBUG
    except KeyError:
      raise KeyError("The start time dictionnary is malformed. It needs to be in the following form: {'format': 'sec-epoch', 'time': 1383842840}")
      
    if (splitStartTime[0] in allowedTimeFormats and splitStartTime[1] in allowedTimeTypes):       #Check that the starttime is correctly formatted
      try:
        if type(startTime['time']) == int:
          return True
        else:
          return False
      except KeyError:
        raise KeyError("The start time dictionnary is malformed. It needs to be in the following form: {'format': 'sec-epoch', 'time': 1383842840}")
    else:
      return False                                       #the startTimeFormat is not correctly formatted
    