"""
packet.py

by Charles Fracchia, Copyright (c) 2013

Packet class module

This class defines data and methods common to all classes.
"""
import warnings, json
from sdipy.sender import Sender
from sdipy.data import Data

class Packet(object):
  """docstring for Packet"""
  
  def __init__(self, **kwargs):
    super(Packet, self).__init__()
    if "address" in kwargs:
      if "startTime" in kwargs:                                    #Forward startTime if it's present in the kwargs
        sender = Sender(kwargs['address'],kwargs['timeFormat'],kwargs['startTime'])
      else:
        sender = Sender(kwargs['address'],kwargs['timeFormat'])    #Instanciate the Sender object with the correct properties
      
      dataPresent = False                       #Check for presence of the Data in the packet
      data = []                                 #Start the data array which cn contain multiple Data objects
      for kwarg in kwargs:                      #Check arguments for data objects
        #print "Types %s" % type(kwargs[kwarg])
        if type(kwargs[kwarg]) == Data:
          data.append(kwargs[kwarg])              #We assume the data packet is valid because it was correctly instanciated. This may be a problem
          dataPresent = True
          
        elif type(kwargs[kwarg]) == list:       #People may be passing more than one data object at a time
          #print "Data field is a list"         #Debug
          for dataObj in kwargs[kwarg]:         #Do this for each Data object in the array
            #print "Now looking at %s" % dataObj.name
            if type(dataObj) == Data:
              data.append(dataObj)          #We assume the data packet is valid because it was correctly instanciated. This may be a problem
              dataPresent = True
            else:
              warnings.warn("You passed something in the data field that is not a data packet. Please instanciate it as an SDIP data packet. \
              See the SDIP Data Class documentation")
              
          #This is to try to instanciate Data packet live.
          #try:
          #  data.psuh(Data.__init__(kwargs[kwarg])        #Initialize the Data object using the array that was passed in
          #  dataPresent = True
          #except KeyError:
          #  warnings.warn("The data packet you provided is malformed. It needs to be a dictionnary with the following structure: {'name':nameval, 'vals':['time':timeval, 'val':val]}")
          
      if not dataPresent:
        raise KeyError("You have not passed any data in, or all the data passed is invalid.")
      
    else:
      raise NameError("You need to provide at least the following values for packets: %s" % ("address","name","vals"))
      
    self.sender = sender
    self.data = data
    
    #Check if formatDetails are being set
  def exportJSON(self):
    """
    Exports an SDIP compatible JSON structure from the self packet object
    Doesn't take anything in
    Outputs an SDIP compatible JSON structure
    """
    pass
    sdipPacket = {
                    "sender":{
                      "address": self.sender.address,
                      "timeFormat": self.sender.timeFormat
                    },
                    "data":[]
                  }
    for dataPacket in self.data:                #Add all the data packets
      sdipPacket['data'].append(\
        {
          'name':dataPacket.name,
          'vals':dataPacket.vals
        }
      )
    
    try:
      if self.sender.startTime != "":           #Pretty bad test for the presence, will fix laterz?
        sdipPacket['sender']['startTime'] = self.sender.startTime
    except AttributeError:                      #Just means that the time is absolute
      absolute = 1
    
    #print sdipPacket                            #DEBUG
    return json.dumps(sdipPacket)
    
  
  def _flattenData(self, data):
    """
    It takes all the values and flattens them in the order they were passed into the object, makes retrieval and data handling by the user easier
    Takes in the data object
    Returns a dictionnary of this form: {'name':DataStreamName, 'x':[x,values], 'y':[y,values]}
    """
    pass
    print "NOT IMPLEMENTED YET :(\n Come back later."