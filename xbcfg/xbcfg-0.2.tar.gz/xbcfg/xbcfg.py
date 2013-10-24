#!/usr/bin/python
# coding: utf-8

"""
Copyright (C) 2013 Lauri Võsandi <lauri.vosandi@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct
import logging
import os
import re
import sys
import serial
import hashlib
import urllib
import zipfile
from time import sleep
from datetime import datetime
import crc16

# XBee device types
DEVICE_TYPES = (
    (0, "Coordinator"),
    (1, "Router"),
    (2, "End device")
)

# IEEE 802.15.4 channels
CHANNEL_FREQUENCIES = {
    11: 2.405,
    12: 2.410,
    13: 2.415,
    14: 2.420,
    15: 2.425,
    16: 2.430,
    17: 2.435,
    18: 2.440,
    19: 2.445,
    20: 2.450,
    21: 2.455,
    22: 2.460,
    23: 2.465,
    24: 2.470,
    25: 2.475,
    26: 2.480
}

RE_EM250_BOOTLOADER = r"""EM250 Bootloader v(?P<version>\d+) b(?P<build>\d+)

1. upload ebl
2. run
3. ebl info
BL >$"""

EM250_UPLOAD_ERRORS = {
    0x21: "The bootloader encountered an error while trying to parse the Start of Header (SOH) character in the XModem frame",
    0x22: "The bootloader detected an invalid checksum in the XModem frame",
    0x23: "The bootloader encountered an error while trying to parse the high byte of the CRC in the XModem frame",
    0x24: "The bootloader encountered an error while trying to parse the low byte of the CRC in the XModem frame",
    0x25: "The bootloader encountered an error in the sequence number of the current XModem frame",
    0x26: "The frame that the bootloader was trying to parse was deemed incomplete (some bytes missing or lost)",
    0x27: "The bootloader encountered a duplicate of the previous XModem frame",
    0x41: "No .ebl header was received when expected",
    0x42: "Header failed CRC",
    0x43: "File failed CRC",
    0x44: "Unknown tag detected in .ebl image",
    0x45: "Invalid .ebl header signature",
    0x46: "Trying to flash odd number of bytes",
    0x47: "Indexed past end of block buffer",
    0x48: "Attempt to overwrite bootloader flash",
    0x49: "Attempt to overwrite SIMEE flash",
    0x4A: "Flash erase failed",
    0x4B: "Flash write failed",
    0x4C: "End tag CRC wrong length",
    0x4D: "Received data before query request/response",
}


FIRMWARE_DIRECTORY = os.path.expanduser("~/.xbee")
FIRMWARE_URL = "http://ftp1.digi.com/support/firmware/82001817_G.zip"
FIRMWARE_MD5 = "13a738453eb001e7e9a58b3ee9aae2ea"

FIRMWARE_EBL_FILES = (
    "XB24-ZB_20A7.ebl",
    "XB24-ZB_21A7.ebl",
    "XB24-ZB_22A7.ebl",
    "XB24-ZB_23A7.ebl",
    "XB24-ZB_26A7.ebl",
    "XB24-ZB_27A7.ebl",
    "XB24-ZB_28A7.ebl",
    "XB24-ZB_29A7.ebl",
    "XB24-ZB_2BA7.ebl"
)

XMODEM_SOH = "\x01"
XMODEM_EOT = "\x04"
XMODEM_ACK = "\x06"
XMODEM_NAK = "\x15"
XMODEM_CAN = "\x18"

def xmodem_crc(block):
    """
    Preliminary pure Python implementation xmodem CRC checksum algorithm
    """
    rem = 0
    for i in range(0, 128):
        rem ^= (ord(block[i]) << 8) & 0xffff
        for j in range(0, 8):
            if rem & 0x8000:
                rem = ((rem << 1) ^ 0x1021) & 0xffff
            else:
                rem = (rem << 1) & 0xffff
    return rem & 0xffff


class RegexException(Exception):
    def __init__(self, regex, string):
        super(RegexException, self).__init__(
            "Could not extract information from '%s' based on regex '%s'" % (
                string, regex))        

class XBeeConfig:
    """
    Class for dealing with XBee AT commands
    """

    AT_COMMANDS = {
        # Addressing commands
        "DH": "Destination address high",
        "DL": "Destination address low",
        "MY": "16-bit network addres",
        "MP": "16-bit parent network address",
        "NC": "Number of remaining children",
        "SH": "Serial number high",
        "SL": "Serial number low",
        "NI": "Node identifier",
        "SE": "Source endpoint",
        "DE": "Destination endpoint",
        "CI": "Cluster identifier",
        "NP": "Maximum RF payload bytes",
        "DD": "Device type identififer",

        # Networking commands
        "CH": "Operating channel",
        "DA": "Force disassociation",
        "ID": "Extended PAN ID",
        "OP": "Operating Extended PAN ID",
        "NH": "Maximum unicast hops",
        "BH": "Maximum broadcast hops",
        "OI": "Operating 16-bit PAN ID",
        "NT": "Node discovery timeout",
        "NO": "Network discovery options",
        "SC": "Scan channels",
        "SD": "Scan duration",
        "ZS": "ZigBee stack profile",
        "NJ": "Node join time",
        "JV": "Channel verification",
        "NW": "Network watchdog timeout",
        "JN": "Join notification",
        "AR": "Aggregate routing notification",
        "DJ": "Disable joining",
        "II": "Initial ID",
        
        # Security commands
        "EE": "Encryption enable",
        "EO": "Encryption options",
        "NK": "Network encryption key",
        "KY": "Link key",

        # RF interfacing commands
        "PL": "Power level",
        "PM": "Power mode",
        "DB": "Received signal strength",
        "PP": "Peak power",

        # Serial interfacing commands
        "AP": "API enable",
        "AO": "API options",
        "BD": "Interface data rate",
        "NB": "Serial parity",
        "SB": "Stop bits",
        "RO": "Packetization timeout",
        "D7": "DIO7 configuration",
        "D6": "DIO6 configuration",
        "IR": "IO sample rate",
        "IC": "IO digital change detection",
        "P0": "PWM0 configuration",
        "P1": "DIO11 configuration",
        "P2": "DIO12 configuration",
        "P3": "DIO13 configuration",
        "D0": "AD0/DIO0 configuration",
        "D1": "AD1/DIO1 configuration",
        "D2": "AD2/DIO2 configuration",
        "D3": "AD3/DIO3 configuration",
        "D4": "AD4/DIO4 configuration",
        "D5": "AD5/DIO5 configuration",
        "D8": "AD8/DIO8 configuration",
        "LT": "Associate LED blink time",
        "PR": "Pull-up resistor",
        "RP": "RSSI PWM timer",
        "%V": "Supply voltage",
        "V+": "Voltage supply monitoring",
        "TP": "Temperature",

        # Diagnostics commands
        "VR": "Firmware version",
        "HV": "Hardware version",
        "AI": "Association indication",

        # AT command options commands
        "CT": "Command mode timeout",
        "CN": "Exit command mode",
        "GT": "Guard times",
        "CC": "Command sequence character",

        # Sleep commands
        "SM": "Sleep mode",
        "SN": "Number of sleep periods",
        "SP": "Sleep period",
        "ST": "Time before sleep",
        "SO": "Sleep options",
        "WH": "Wake host",
        "SI": "Sleep immediately",
        "PO": "Polling rate",

        # Execution commands
        "AC": "Apply changes",
        "WR": "Write",
        "RE": "Restore defaults",
        "FR": "Software reset",
        "NR": "Network reset",
        "SI": "Sleep immediately",
        "CB": "Commissioning pushbutton",
        "ND": "Node discover",
        "DN": "Destination node",
        "IS": "Force sample",
        "1S": "XBee sensor sample"
    }

    BAUD_RATES = (
        (0, 1200),
        (1, 2400),
        (2, 4800),
        (3, 9600),
        (4, 19200),
        (5, 38400),
        (6, 57600),
        (7, 115200),
        (8, 230400)
    )

    # XBee (S2) power levels
    POWER_LEVELS = (
        (0, -8),
        (1, -4),
        (2, -2),
        (3,  0),
        (4,  2)
    )
    
    ASSOCIATION_INDICATOR = {
        0x00: "Successfully formed or joined a network",
        0x21: "Scan found no PANs",
        0x22: "Scan found no valid PANs based on current SC and ID settings",
        0x23: "Valid coordinator or router found, but they are not allowing joining",
        0x24: "No joinable beacons were found",
        0x25: "Unexpected state, node should not be attempting to join at this time",
        0x27: "Node joining attempt failed, perhaps incorrect encryption key?",
        0x2a: "Coordinator start attempt failed",
        0x2b: "Checking for an existing coordinator",
        0x2c: "Attempt to leave the network failed",
        0xab: "Attempted to join a device that did not respond",
        0xac: "Secure join error, network security key received unsecured",
        0xad: "Secure join error, network security key not received",
        0xaf: "Secure join error, joining device does not have the right preconfigured link key",
        0xff: "Scanning for a ZigBee network"
    }

    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        """
        Construct XBeeConfig instance, note that serial port is not opened yet.
        """
        self.port = port
        self.baudrate = baudrate
        self.handle = None

    def info(self, msg):
        """
        Log message at info level
        """
        if self.handle:
            logging.info("%s@%d: %s" % (self.handle.port, self.handle.baudrate, msg))
        else:
            logging.info(msg)

    def debug(self, msg):
        """
        Log message at debug level
        """
        if self.handle:
            logging.debug("%s@%d: %s" % (self.handle.port, self.handle.baudrate, msg))
        else:
            logging.debug(msg)

    def connect(self, baudrate=None):
        """
        Open serial connection or reset baudrate
        """
        if self.handle:
            self.info("Re-negotiating serial link")
            self.handle.close()
        self.handle = serial.Serial(
            self.port,
            baudrate=baudrate or self.baudrate,
            timeout=1)

    def at_enter(self):
        """
        Enter AT command mode
        """
        self.info("Entering AT mode")
        
        self.read()

        # TODO: Detect API mode

        # Try to write exit AT mode command in case we are already in AT mode
        self.write("ATCN")
        self.read()
        sleep(1)

        # Try to enter AT mode again
        self.write("+++", append_newline=False)
        sleep(1)
        self.read("OK")

        self.attention()

    def attention(self):
        """
        Confirm AT command mode
        """
        self.write("AT")
        self.read("OK")

    def write(self, j, append_newline=True, binary=False):
        """
        Write buffer to serial port
        """
        self.debug("Writing: %s" % (" ".join(["%02x" % ord(i) for i in j]) if binary else j))
        if not binary and append_newline:
            j += "\r"
        self.handle.write("%s" % j)

    def read(self, assert_output=None, delay=0.2, preserve_newlines=False):
        """
        Read buffer from serial port
        """
        if delay:
            sleep(delay)
        output = ""
        while self.handle.inWaiting() > 0:
            output += self.handle.read(1)
        output = output.replace("\r", "\n")
        if not preserve_newlines:
            output = output.strip()
        self.debug("Reading: %s" % output.strip())
        if assert_output:
            assert assert_output==output, \
                "Expected output '%s' was not found in:\n'%s'" % (assert_output, output)
        return output

    def firmware_version(self):
        """
        Return firmware version
        """
        self.write("ATVR")
        output = self.read()
        return [int(j, 16) for j in output]

    def hardware_version(self):
        """
        Return hardware version
        """
        self.write("ATHV")
        output = self.read()
        return int(output[:2], 16), int(output[2:], 16)

    def temperature(self):
        """
        Return temperature for XBee **PRO** modules
        """
        self.write("ATTP")
        return self.read()

    def restore_defaults(self):
        """
        Restore firmware configuration defaults
        """
        self.info("Restoring defaults")      
        self.write("ATRE")
        self.read("OK")

    def serial_number(self):
        """
        Return serial number the module
        """
        self.write("ATSH")
        sh = self.read()
        assert re.match("[0-9A-F]{1,8}", sh), "Invalid value '%s'" % sh
        self.write("ATSL")
        sl = self.read()
        assert re.match("[0-9A-F]{1,8}", sl), "Invalid value '%s'" % sl
        return int(sh, 16) << 32 | int(sl, 16)

    def destination_address(self):
        """
        Get destination address
        """
        self.write("ATDH")
        dh = self.read()
        assert re.match("[0-9A-F]{1,8}", dh), "Invalid value '%s'" % dh
        self.write("ATDL")
        dl = self.read()
        assert re.match("[0-9A-F]{1,8}", dl), "Invalid value '%s'" % dl
        return int(dh, 16) << 32 | int(dl, 16)
        
    def set_destination_address(self, value):
        self.info("Setting destination address: %s" % repr(value))
        dl = value & 0xffffffff
        dh = (value >> 32) & 0xffffffff
        self.write("ATDH %x" % dh)
        self.read("OK")
        self.write("ATDL %x" % dl)
        self.read("OK")

    def baud_rate(self):
        """
        Get baud rate
        """
        self.write("ATBD")
        bd = self.read()
        assert re.match("[0-8]", bd), "Invalid value '%s'" % bd
        return dict(self.BAUD_RATES)[int(bd)]

    def channel(self):
        """
        Get channel
        """
        self.write("ATCH")
        ch = self.read()
        assert re.match("[0-9A-F]{1,2}", ch), "Invalid value '%s'" % ch
        return int(ch, 16)

    def set_channel(self, value):
        """
        Set channel
        """
        self.info("Setting channel to %s" % value)
        assert 0x0b <=  value <= 0x1a, "Invalid channel 0x%02x, expected 0x0b-0x1a" % value
        self.write("ATCH %02x" % value)
        self.read("OK")

    def network_identifier(self):
        """
        Get or set network identifier
        """
        self.write("ATID")
        id = self.read()
        assert re.match("[0-9A-F]{1,4}", id), "Invalid value '%s'" % id
        return int(id, 16)
        
    def set_network_identifier(self, value):
        self.info("Setting network identifer to 0x%04x" % value)
        assert 0x0000 <= value <= 0xffff, "Invalid network identifier: %04x" % value
        self.write("ATID %x" % value)
        self.read("OK")

    def encryption_enabled(self):
        """
        Get or set whether encryption is enabled or not
        """
        self.write("ATEE")
        ee = self.read()
        assert re.match("[01]", ee), "Invalid value '%s'" % ee
        return int(ee)

    def set_encryption_enabled(self, value):
        """
        Set encryption enabled
        """
        self.info("Enabling encryption" if value else "Disabling encryption")
        assert 0 <= value <= 1, "Invalid value"
        self.write("ATEE %x" % value)
        self.read("OK")
        
    def enable_encryption(self):
        self.set_encryption_enabled(True)
        
    def disable_encryption(self):
        self.set_encryption_enabled(True)

    def set_encryption_key(self, value):
        """
        Set encryption key
        """
        self.info("Setting encryption key: 0x%08x" % value)
        assert 0 <= value <= 0xffffffffffffffffffffffffffffffff, "Invalid encryption key: %032x" % value
        self.write("ATKY %x" % value)
        self.read("OK")

    def node_identifier(self):
        """
        Get node identifier
        """
        self.write("ATNI")
        ni = self.read()
        return ni
        
    def set_node_identifier(self, value):
        self.info("Setting node identifer to %s" % value)
        assert isinstance(value, str), "Invalid node identifier data type"
        assert 1<=len(value)<=20, "Invalid node identifer length"
        assert not value.startswith(" "), "Identifier node can't start with space"
        self.write("ATNI %s" % value)
        self.read("OK")

    def node_discover_timeout(self):
        """
        Get node discover timeout
        """
        self.write("ATNT")
        nt = self.read()
        return int(nt, 16) * 0.100

    def set_node_discover_timeout(self, value):
        """
        Set node discover timeout between 3.2 and 1200 seconds
        """
        self.info("Setting node discover timeout to %d" % value)
        value = int(value / 0.100)
        assert 0x20 <= value <= 0x2ee0, "Invalid discover timeout"
        self.write("ATNT %x" % value)
        self.read("OK")

    def power_level(self):
        """
        Get power level
        """
        self.write("ATPL")
        pl = self.read()
        return dict(self.POWER_LEVELS)[int(pl, 16)]
       
    def set_power_level(self):
        """
        Set power level
        """
        assert 0 <= value <= 4, "Invalid power level"
        self.write("ATPL %x" % value)
        self.read("OK")

    def node_discover(self):
        """
        Return list of discovered nodes:
        (serial high, serial low), node identifier, device type, profile id, manufacturer id
        """
        node_discover_timeout = self.node_discover_timeout()
        self.write("ATNO 3")
        self.read("OK")
        self.write("ATND")
        sleep(node_discover_timeout)
        buf = self.read()

        for node in buf.split("\n\n"):
            node += "\n"
            try:
                marker, sh, sl, ni, parent_network_address, device_type, \
                status, profile_id, manufacturer_id, _ = node.split("\n", 9)
            except ValueError:
                assert False, "Invalid node: '%s'" % node
            assert re.match("[0-9A-F]{8}", sh), "Invalid SH: %s" % sh
            assert re.match("[0-9A-F]{8}", sl), "Invalid SL: %s" % sh
            assert re.match("[\w ]{1,20}", ni), "Invalid node identifier: %s" % ni
            assert re.match("0[012]", device_type), "Invalid device type: %s" % device_type
            assert re.match("[0-9A-F]{2}", status), "Invalid status: %s" % status
            assert re.match("[0-9A-F]{2}", profile_id), "Invalid profile id: %s" % status
            assert re.match("[0-9A-F]{2}", manufacturer_id), "Invalid manufacturer id: %s" % status
            yield (int(sh,16) << 32 | int(sl,16)), ni, int(device_type,16), int(profile_id,16), int(manufacturer_id,16)
            
    def force_disassociate(self):
        self.info("Forcing disassociation")
        self.write("ATDA")
        self.read("OK")

    def write_changes(self):
        """
        Write configuration changes
        """
        self.info("Writing changes")
        self.write("ATWR")
        self.read("OK")

    def supply_voltage(self):
        """
        Return supply voltage (mV)
        """
        self.write("AT%V")
        return int(self.read(), 16) * 1200 / 1024

    def reset(self):
        """
        Reset XBee module
        """
        self.info("Resetting")
        self.write("ATFR")
        self.read("OK")

    def apply_changes(self):
        """
        Apply configuration changes
        """
        self.info("Applying changes")
        self.write("ATAC")
        self.read("OK")

    def at_exit(self):
        """
        Exit AT command mode
        """
        self.write("ATCN")
        self.read("OK")
        
    def association_indication(self):
        """
        Return assocation indication
        """
        self.write("ATAI")
        return self.ASSOCIATION_INDICATOR[int(self.read(), 16)]

    def probe(self):
        """
        Probe for undocumented AT commands
        """
        for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789%":
            for j in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789%":
                cmd = "AT" + i + j
                # Ignore:
                # AT%P - jump to bootloader
                # ATCN - exit command line
                # ATFR - firmware reset
                if cmd in ("AT%P","ATCN", "ATFR"): 
                    continue

                self.write(cmd)
                value = self.read()
                if value != "ERROR":
                    print cmd,
                    if cmd[2:] in self.AT_COMMANDS:
                        print "(%s)" % self.AT_COMMANDS[cmd[2:]],
                    else:
                        print "(??)",
                    print "==>",
                    print repr(value)
                elif cmd[2:] in self.AT_COMMANDS:
                    print cmd,
                    print "(%s)" % self.AT_COMMANDS[cmd[2:]],
                    print "==>",
                    print repr(value)
    
    def bootloader_enter(self):
        """
        Jump into the bootloader using undocumented AT%P command
        """
        self.write("AT%P")
        self.read("OK")

        self.info("Successfully issued jump into bootloader AT command")

        self.handle.close()
        sleep(0.1)

        self.info("Switching baud rate")


        command_mode_baudrate = self.handle.baudrate

        self.bootloader_validate()

    def bootloader_validate(self):
        """
        Validate the state, that we are actually in the bootloader
        """
        self.info("Attempting to talk to the bootloader ...")
        self.connect(115200)
        buf = None

        for j in range(1,50):
            self.write("\r")
            sleep(0.1)
            buf = self.read().strip()
            if buf:
                break

        if not buf:
            raise Exception("Waiting for bootloader prompt timed out!")

        buf = buf.replace("\0", "").replace("\r\n", "\n").replace("\n\n", "\n").strip()
        m = re.match(RE_EM250_BOOTLOADER, buf, re.M|re.S|re.DOTALL)
        if not m:
            raise Exception("Unknown bootloader prompt: %s" % buf)
        else:
            self.info("Successfully opened bootloader prompt")

    def bootloader_flash(self, filename):
        """
        Flash firmware
        """
        self.info("About to flash firmware from %s" % filename)
        self.bootloader_validate()
        self.write("1\r")
        sleep(0.2)
        self.read()

        BLOCK_SIZE = 128

        
        fh = open(filename, "rb")
        firmware = fh.read()
        fh.close()
        self.info("Read file size %d bytes" % len(firmware))

        # Calculate required padding
        padding = BLOCK_SIZE - len(firmware) % BLOCK_SIZE
        if padding == BLOCK_SIZE:
            padding = 0
        self.info("Padding with %d bytes" % padding)
        assert 0 <= padding < BLOCK_SIZE, "Invalid padding"

        # Append 0xFF bytes as padding
        firmware += padding * "\xff"
        assert len(firmware) % BLOCK_SIZE == 0, "Invalid padded size"

        # Calculate block count
        block_count = len(firmware) / BLOCK_SIZE
        self.info("Padded size %d bytes (%d blocks)" % (
            len(firmware), block_count))

        for block_index in range(0, block_count):
            block = firmware[block_index*BLOCK_SIZE:(block_index+1)*BLOCK_SIZE]
            self.write(XMODEM_SOH, binary=True)
            self.write(struct.pack("BB",
                (block_index+1) % 256, (254-block_index) % 256), binary=True)
            self.write(block, binary=True)
            checksum = crc16.crc16xmodem(block)
            self.debug("Checksum: %02x" % checksum)
            self.write(struct.pack(">H", checksum), binary=True)
            while self.handle.inWaiting() == 0:
                pass
            ack = self.handle.read(1)
            assert self.handle.inWaiting() == 0, "Bytes still waiting in buffer!"
            if ack != "\x06":
                raise Exception("Failed to transfer block %d, reason %s" % (
                    block_index, " ".join(["%02x" % ord(j) for j in ack])))
        self.write(XMODEM_EOT, binary=True)
        while self.handle.inWaiting() == 0:
            pass
        ack = self.handle.read(1)
        if ack != "\x06":
            raise Exception("Failed to read programming confirmation")
        response = self.read()
        if "Serial upload complete" not in response:
            raise Exception("Got unknown response: %s" % response)

    def bootloader_exit(self):
        """
        Exit bootloader
        """
        self.bootloader_validate()
        self.info("Jumping from bootloader to firmware")
        self.write("2\r")
        self.read()
        self.connect()
        sleep(2)
        self.at_enter()
 
    def maximum_payload(self):
        """
        Get maximum payload
        """
        self.write("ATNP")
        return int(self.read(), 16)
        
    def packetization_timeout(self):
        """
        Get packetization timeout
        """
        self.write("ATRO")
        return int(self.read(), 16)
        
    def set_packetization_timeout(self, value):
        """
        Set packetization timeout
        """
        assert 0 <= value <= 0xff, "Invalid packetization timeout 0x%02x" % value
        self.write("ATRO %02x" % value)
        self.read("OK")

def main(command, *remainder):
    import argparse
    parser = argparse.ArgumentParser(
        prog="%s %s" % (sys.argv[0], command),
        description="XBee configuration and flashing utility")
    parser.add_argument(
        "--verbosity", "-v",
        metavar="LEVEL",
        default="error",
        choices=("info", "debug", "error"),
        help="Set verbosity (info, debug)")
    
    def hexint(mixed):
        if isinstance(mixed, basestring):
            if mixed.startswith("0x"):
                mixed = int(mixed[2:], 16)
        if isinstance(mixed, int):
            return mixed
        raise argparse.ArgumentTypeError("Invalid value %s" % mixed)
    
    if command is not "download":
        parser.add_argument(
            "--device", "-d",
            default="/dev/ttyUSB0",
            help="Serial port")
        parser.add_argument(
            "--baud", "-b",
            default=9600, type=int,
            help="Initial baudrate for serial connection")
    if command == "reset":
        parser.add_argument(
            "--destination-address", "-da",
            default=0x000000000000ffff,
            metavar="ADDRESS",
            type=hexint,
            help="Destination address (64-bit integer), defaults to broadcast")
        parser.add_argument(
            "--channel", "-ch",
            default=0x0c,
            type=hexint,
            metavar="CHANNEL",
            help="Channel (11-26)")
        parser.add_argument(
            "--node-identifier", "-ni",
            default="XB-%(serial)016x",
            metavar="ID",
            help="Node identifier (20-character ASCII string)")
        parser.add_argument(
            "--network-identifier", "-id",
            default=0x3332,
            type=hexint,
            metavar="0x3332",
            help="Network identifier (16-bit integer)")
        parser.add_argument(
            "--enable-encryption", "-ee",
            action="store_true",
            default=False,
            help="Enable encryption")
        parser.add_argument(
            "--encryption-key", "-psk",
            default=0xdeadc0de,
            type=hexint,
            metavar="0xDEADC0DE",
            help="Encryption key (32-bit integer)")
        parser.add_argument(
            "--node-discover-timeout", "-nd",
            metavar="SECONDS",
            default=4,
            type=int)
            
    if command == "flash":
        parser.add_argument(
            "--assume-bootloader-prompt",
            default=False,
            action="store_true",
            help="Assume that the bootloader prompt has been opened already, eg. by DTR-RTS-DIN wiring")
        parser.add_argument(
            "--operation", "-o",
            default="router",
            choices=("coordinator", "router", "end-device"),
            help="Operation mode (coordinator, router, end-device)")
        parser.add_argument(
            "--enable-api",
            default=False,
            action="store_true",
            help="Flash firmware which boots into the API mode")

    args = parser.parse_args(remainder)
    
    logging.basicConfig(level=getattr(logging, args.verbosity.upper()))
    
    if command in ("download", "flash"):
        zip_filename = os.path.join(FIRMWARE_DIRECTORY, os.path.basename(FIRMWARE_URL))
       
        if not os.path.isfile(zip_filename):
            if not os.path.isdir(FIRMWARE_DIRECTORY):
                os.makedirs(FIRMWARE_DIRECTORY)
            print "Fetching", FIRMWARE_URL, "to", zip_filename
            buf = ""
            fh = urllib.urlopen(FIRMWARE_URL)
            while True:
                sys.stdout.write(".")
                sys.stdout.flush()
                chunk = fh.read(32768)
                buf += chunk
                if len(buf) % 2**18 == 0:
                    sys.stdout.write(" ")
                    sys.stdout.flush()
                if len(buf) % 2**20 == 0 or not chunk:
                    sys.stdout.write(" %d kB\n" % (len(buf) / 1024))
                    sys.stdout.flush()
                if not chunk:
                    break
            fh.close()

            fh = open(zip_filename, "wb")
            fh.write(buf)
            fh.close()


        fh = open(zip_filename, "rb")
        checksum = hashlib.md5()
        while True:
            buf = fh.read(32768)
            if not buf:
                break
            checksum.update(buf)
            
        if FIRMWARE_MD5 and checksum.hexdigest() != FIRMWARE_MD5:
            raise ValueError("Invalid checksum %032x, expected %032x" % (
                checksum.hexdigest(), FIRMWARE_MD5))

        zf = None
        
        for filename in FIRMWARE_EBL_FILES:
            if os.path.isfile(os.path.join(FIRMWARE_DIRECTORY, "ebl_files", filename)):
                continue
            print "Extracting:", filename
            if not zf:
                zf = zipfile.ZipFile(zip_filename)
            zf.extract("ebl_files/%s" % filename, FIRMWARE_DIRECTORY)

        if command == "download":
            return
    
    xbee = XBeeConfig(args.device, args.baud)

    if command == "flash":
        if not args.assume_bootloader_prompt:
            xbee.connect()
            xbee.at_enter()
            xbee.bootloader_enter()
        j = {"coordinator":0, "router":2,"end-device":8}[args.operation]
        if args.enable_api:
            print "You're about to flash firmware which boots into the API mode."
            print "This utility does not support talking to modules in API mode yet!"
            j += 1
        firmware_filename = os.path.join(FIRMWARE_DIRECTORY, "ebl_files/XB24-ZB_2%dA7.ebl" % j)
        print "You're about to flash: %s" % firmware_filename
        try:
            raw_input("Press Enter to continue or Ctrl-C to bail out like a wimp!")
            xbee.bootloader_flash(firmware_filename)
            print "Successful flash, restarting firmware"
        except KeyboardInterrupt:
            print "Ha-ha!"
        finally:
            xbee.bootloader_exit()
        return

    xbee.connect()
    xbee.at_enter()
    
    if command == "bootloader":
        xbee.bootloader_enter()
        return 
        
    if command == "status":
        """
        Dump current configuration and status
        """
        serial_number = xbee.serial_number()
        node_discover_timeout = xbee.node_discover_timeout()
        
        print "Module status"
        print "============="
        print "Association indication:", xbee.association_indication()
        channel = xbee.channel()
        if channel:
            print "Channel: 0x%02x (%.3f GHz)" % (channel, CHANNEL_FREQUENCIES[channel])
        else:
            print "Channel: not operating on any channel, device has not joined PAN"
        print "Supply voltage: %d mV (2100-3600mV ok)" % xbee.supply_voltage()
            
        print
        print "Module configuration"
        print "===================="
        print "Network idenfitier: 0x%04x" % xbee.network_identifier()
        print "Node idenfier: %s" % xbee.node_identifier()
        print "Packetization timeout: %d sec" % xbee.packetization_timeout()
        print "Node discover timeout: %.02f sec" % node_discover_timeout
        print "Baud rate:", xbee.baud_rate()
        print "Encryption enabled: %s" % bool(xbee.encryption_enabled())
        print "Power level: %.02f dBm" % xbee.power_level()
        print "Destination address: 0x%016x" % xbee.destination_address()

        print
        print "Module information"
        print "=================="
        print "Serial number: 0x%016x" % xbee.serial_number()
        print "Maximum payload: %s bytes" % xbee.maximum_payload()
        module_type, revision = xbee.hardware_version()
        print "Hardware version: 0x%02x%02x" % (module_type, revision)

        print "  Module type:",        
        if module_type == 0x19:
            print "XBee"
        elif module_type == 0x1a:
            print "Xbee-PRO"
        else:
            print "Unknown"
        print "  Revision: %d" % revision

        # Firmware version
        variant, operation, version, revision = xbee.firmware_version()
        print "Firmware version: 0x%x%x%x%x" % (variant, operation, version, revision)

        print "  Variant:",
        if variant == 1:
            print "ZNet only"
        elif variant == 2:
            print "ZigBee compatible"
        else:
            print "Unknown"

        print "  Operation:",
        if operation >= 0 and operation <= 1:
            print "Coordinator,",
        elif operation >= 2 and operation <= 3:
            print "Router,",
        elif operation >= 8 and operation <= 9:
            print "End device,",
        else:
            print "Unknown,",


        if operation % 2 == 0:
            print "transparent operation"
        else:
            print "API operation"

        print "  Version: %d" % version
        print "  Revision: %d" % revision
        xbee.at_exit()
        return

    if command == "reset":
        print "Restoring defaults ..."
        xbee.restore_defaults()
        xbee.set_node_identifier(
            args.node_identifier % {"serial":xbee.serial_number()})
        xbee.set_destination_address(
            args.destination_address)
        xbee.set_network_identifier(
            args.network_identifier)
        xbee.set_node_discover_timeout(
            args.node_discover_timeout)
        xbee.set_encryption_enabled(
            args.enable_encryption)
        xbee.set_encryption_key(
            args.encryption_key)

        xbee.write_changes()
        xbee.apply_changes()
        xbee.reset()
        print "Restarting firmware ..."
        return

    if command == "discover":
        print "Discovering other nodes..."
        for node in xbee.node_discover():
            serial_number, node_identifier, device_type, _, _ = node
            print "%016x %s %s" % (serial_number, dict(DEVICE_TYPES)[device_type], node_identifier)
        xbee.at_exit()
        return
        
    raise KeyError()
        
if __name__ == '__main__':
    args = sys.argv[1:]
    try:
        if not args:
            raise KeyError()
        main(*args)
    except KeyError:
        print "usage: %s reset|bootloader|download|flash|reset [extra arguments]" % sys.argv[0]
        print
        print "XBee configuration and flashing utility"
        exit(255)


