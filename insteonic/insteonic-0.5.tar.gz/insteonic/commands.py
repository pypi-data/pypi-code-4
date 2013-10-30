import binascii
import sys


class StandardCommand(object):
    """ The standard insteon comand.
        It consists of eight bits as
        described in the below dictionary """
    
    description = "No description available"
    arguments = []
    message_flags = '00'
    command1 = '00'
    command2 = '00'

    bytes = {
        1: '02', #Start of command string
        2: '62', #Direct command indicator
        3: '00', #Device ID part 1
        4: '00', #Device ID part 2
        5: '00', #Device ID part 3
        6: '00', #message flags
        7: '00', #command1
        8: '00', #command2
    }
    
    def __init__(self, **kwargs):
        self.bytes[6] = self.message_flags
        self.bytes[7] = self.command1
        self.bytes[8] = self.command2
        
    def get_command_string(self, device_id='000000'):
        """ Assembles the required message bytes
            into a single hexidecimal string"""
            
        self.bytes[3] = device_id[:2]
        self.bytes[4] = device_id[2:4]
        self.bytes[5] = device_id[4:6]
        return ''.join(self.bytes.values())
        
    def get_raw_command_string(self, device_id='000000'):
        """ Takes the assembled hexidecimal string
            and converts it into a string of raw ascii
            bytes to use in serial commands"""
        
        self.get_command_string(device_id)
        return ''.join([str(binascii.unhexlify(v)) for v in self.bytes.values()])

    def handle_response(self, response_str):
        """ A handler for the response 
            The last byte should be 06, 
            which indicates success """
        
        result_code = binascii.hexlify(response_str)[-2:]
        
        try:
            result = int(result_code)
        except:
            pass
            
        if result == 6:
            self.success()
        
        else:
            self.error(result_code)

    def success(self):
        """A callback to handle a successful command """
        
        print "success"

    def error(self, error_code=None):
        """A callback to handle a successful command """
        print "error"


class ExtendedCommand(StandardCommand):
    """ The extended insteon comand.
        It consists of 22 bytes and depends
        on the target device """    
    
    extended_bytes = {
        9:  '00',
        10: '00',
        11: '00',
        12: '00',
        13: '00',
        14: '00',
        15: '00',
        16: '00',
        17: '00',
        18: '00',
        19: '00',
        20: '00',
        21: '00',
        22: '00',
    }
    
    def __init__(self, **kwargs):
        super(ExtendedCommand, self).__init__()
        self.bytes = dict(self.bytes.items() + self.extended_bytes.items())
        
class On(StandardCommand):
    """ Sends the on command to the device"""
    
    description = "Turn the device on"
    message_flags = '0F'
    command1 = '11'
    command2 = 'FF'


class Off(On):
    """ Sends the off commands to the device """
    
    description = "Turn the device off"
    command1 = '13'
    
class OnTo(On):
    """ Brightens the device to the
        specified level """
        
    description = "Turn the device on and set the brightness to the specified level"
    
    def __init__(self, **kwargs):
        self.command2 = str(int(kwargs['level'], 16))
        super(OnTo, self).__init__(**kwargs)
        
        
class Brighten(On):
    """ Raise the brightness leve one step """
    
    description = "Raise the brightness one step"
    command1 = '15'
    
class Dim(On):
    """ Lower the brightness level one step """

    description = "Lower the brightness level one step"
    command1 = '16'



class ThermostatCommand(ExtendedCommand):
    """ A base command for Insteon thermostats """
    message_flags = '1F'
    command1 = '6B'
    
    def __init__(self, **kwargs):

        try:
            self.set_last_byte()
        except:
            pass
        
        super(ThermostatCommand, self).__init__(**kwargs)
        
    def set_last_byte(self):
        
        last_byte = 256 - (int(self.command1, 16) + int(self.command2, 16))        

        if last_byte < 0:
            last_byte = 512 - (int(self.command1, 16) + int(self.command2, 16))  
            

        last_byte = hex(last_byte).replace('0x', '').upper()
                
        if len(last_byte) == 1:
            last_byte = '0%s' % last_byte

        self.extended_bytes[22] = last_byte


class ThermostatSetHeat(ThermostatCommand):
    """ Set the thermostat mode to heat """
    description = "Set the mode to HEAT"
    command2 = '04'
    

class ThermostatSetCool(ThermostatCommand):
    """ Set the thermostat mode to cool """
    description = "Set the mode to COOL"
    command2 = '05'
    

class ThermostatSetAuto(ThermostatCommand):
    """ Set the thermostat mode to auto """
    description = "Set the mode to AUTO"
    command2 = '06'
    
    
class ThermostatFanOn(ThermostatCommand):
    """ Set the thermostat fan to on """
    description = "Turn the fan ON"
    command2 = '07'
    
        
class ThermostatFanAuto(ThermostatCommand):
    """ Set the thermostat fan to auto """
    description = "Set the fan to AUTO"
    command2 = '08'
    

class ThermostatSetOff(ThermostatCommand):
    """ Turn the thermostat off """
    description = "Turn the device OFF"
    command2 = '09'
    
    
class ThermostatSetProgramHeat(ThermostatCommand):
    """ Set the thermostat to mode to Program Heat"""
    description = "Set the mode to PROGRAM HEAT"
    command2 = '0A'
    
    
class ThermostatSetProgramCool(ThermostatCommand):
    """ Set the thermostat to mode to Program Cool"""
    description = "Set the mode to PROGRAM COOL"
    command2 = '0B'
    
class ThermostatSetProgramAuto(ThermostatCommand):
    """ Set the thermostat to mode to Program Auto"""
    description = "Set the mode to PROGRAM AUTO"
    command2 = '0C'
    
class ThermostatEnableStatusChangeMessage(ThermostatCommand):
    """ Enable the broadcasting of a message whenever the mode changes """
    description = "Enable notifications when the mode changes"
    command2 = '16'
    
class ThermostatDisableStatusChangeMessage(ThermostatCommand):
    """ Disable the broadcasting of a message whenever the mode changes """
    description = "Disable notifications when the mode changes"
    command2 = '17'
    
    
class ThermostatSetCoolPoint(ThermostatCommand):
    """ Sets the temperature at which the
        system will begin cooling.
        
        Takes one integer argument: temperature. """
        
    description = "Set the temperature at the the system will begin cooling"
    command1 = '6C'
    command2 = None
    
    def __init__(self, **kwargs):
        
        try:
            temperature = int(kwargs.get('temperature'))
        except:
            sys.exit("Invalid temperature")
        
        try:
            base = temperature * 2
            self.command2 = hex(base).replace('0x', '').upper()
        except:
            pass

        super(ThermostatSetCoolPoint, self).__init__(**kwargs)

class ThermostatSetHeatPoint(ThermostatSetCoolPoint):
    """ Sets the temperature at which the
        system will begin heating.
        
        Takes one integer argument: temperature. """
    description = "Set the temperature at the the system will begin heating."
    command1 = '6D'

