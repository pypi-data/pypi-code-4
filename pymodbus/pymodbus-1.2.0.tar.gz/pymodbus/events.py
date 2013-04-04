'''
Modbus Remote Events
------------------------------------------------------------

An event byte returned by the Get Communications Event Log function
can be any one of four types. The type is defined by bit 7
(the high-order bit) in each byte. It may be further defined by bit 6.
'''
from pymodbus.exceptions import NotImplementedException
from pymodbus.exceptions import ParameterException
from pymodbus.utilities import pack_bitstring, unpack_bitstring


class ModbusEvent(object):

    def encode(self):
        ''' Encodes the status bits to an event message

        :returns: The encoded event message
        '''
        raise NotImplementedException()

    def decode(self, event):
        ''' Decodes the event message to its status bits

        :param event: The event to decode
        '''
        raise NotImplementedException()


class RemoteReceiveEvent(ModbusEvent):
    ''' Remote device MODBUS Receive Event

    The remote device stores this type of event byte when a query message
    is received. It is stored before the remote device processes the message.
    This event is defined by bit 7 set to logic '1'. The other bits will be
    set to a logic '1' if the corresponding condition is TRUE. The bit layout
    is::

        Bit Contents
        ----------------------------------
        0   Not Used
        2   Not Used
        3   Not Used
        4   Character Overrun
        5   Currently in Listen Only Mode
        6   Broadcast Receive
        7   1
    '''

    def __init__(self, **kwargs):
        ''' Initialize a new event instance
        '''
        self.overrun   = kwargs.get('overrun', False)
        self.listen    = kwargs.get('listen', False)
        self.broadcast = kwargs.get('broadcast', False)

    def encode(self):
        ''' Encodes the status bits to an event message

        :returns: The encoded event message
        '''
        bits  = [False] * 3
        bits += [self.overrun, self.listen, self.broadcast, True]
        packet = pack_bitstring(bits)
        return packet

    def decode(self, event):
        ''' Decodes the event message to its status bits

        :param event: The event to decode
        '''
        bits = unpack_bitstring(event)
        self.overrun   = bits[4]
        self.listen    = bits[5]
        self.broadcast = bits[6]


class RemoteSendEvent(ModbusEvent):
    ''' Remote device MODBUS Send Event

    The remote device stores this type of event byte when it finishes
    processing a request message. It is stored if the remote device
    returned a normal or exception response, or no response.

    This event is defined by bit 7 set to a logic '0', with bit 6 set to a '1'.
    The other bits will be set to a logic '1' if the corresponding
    condition is TRUE. The bit layout is::

        Bit Contents
        -----------------------------------------------------------
        0   Read Exception Sent (Exception Codes 1-3)
        1   Slave Abort Exception Sent (Exception Code 4)
        2   Slave Busy Exception Sent (Exception Codes 5-6)
        3   Slave Program NAK Exception Sent (Exception Code 7)
        4   Write Timeout Error Occurred
        5   Currently in Listen Only Mode
        6   1
        7   0
    '''

    def __init__(self, **kwargs):
        ''' Initialize a new event instance
        '''
        self.read          = kwargs.get('read', False)
        self.slave_abort   = kwargs.get('slave_abort', False)
        self.slave_busy    = kwargs.get('slave_busy', False)
        self.slave_nak     = kwargs.get('slave_nak', False)
        self.write_timeout = kwargs.get('write_timeout', False)
        self.listen        = kwargs.get('listen', False)

    def encode(self):
        ''' Encodes the status bits to an event message

        :returns: The encoded event message
        '''
        bits = [self.read, self.slave_abort, self.slave_busy,
            self.slave_nak, self.write_timeout, self.listen]
        bits  += [True, False]
        packet = pack_bitstring(bits)
        return packet

    def decode(self, event):
        ''' Decodes the event message to its status bits

        :param event: The event to decode
        '''
        # todo fix the start byte count
        bits = unpack_bitstring(event)
        self.read          = bits[0]
        self.slave_abort   = bits[1]
        self.slave_busy    = bits[2]
        self.slave_nak     = bits[3]
        self.write_timeout = bits[4]
        self.listen        = bits[5]


class EnteredListenModeEvent(ModbusEvent):
    ''' Remote device Entered Listen Only Mode

    The remote device stores this type of event byte when it enters
    the Listen Only Mode. The event is defined by a content of 04 hex.
    '''

    value = 0x04
    __encoded = '\x04'

    def encode(self):
        ''' Encodes the status bits to an event message

        :returns: The encoded event message
        '''
        return self.__encoded

    def decode(self, event):
        ''' Decodes the event message to its status bits

        :param event: The event to decode
        '''
        if event != self.__encoded:
            raise ParameterException('Invalid decoded value')


class CommunicationRestartEvent(ModbusEvent):
    ''' Remote device Initiated Communication Restart

    The remote device stores this type of event byte when its communications
    port is restarted. The remote device can be restarted by the Diagnostics
    function (code 08), with sub-function Restart Communications Option
    (code 00 01).

    That function also places the remote device into a 'Continue on Error'
    or 'Stop on Error' mode. If the remote device is placed  into 'Continue on
    Error' mode, the event byte is added to the existing event log. If the
    remote device is placed into 'Stop on Error' mode, the byte is added to
    the log and the rest of the log is cleared to zeros.

    The event is defined by a content of zero.
    '''

    value = 0x00
    __encoded = '\x00'

    def encode(self):
        ''' Encodes the status bits to an event message

        :returns: The encoded event message
        '''
        return self.__encoded

    def decode(self, event):
        ''' Decodes the event message to its status bits

        :param event: The event to decode
        '''
        if event != self.__encoded:
            raise ParameterException('Invalid decoded value')
