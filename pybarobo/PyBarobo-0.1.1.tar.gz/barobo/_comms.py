#!/usr/bin/env python

import socket
try:
  import serial
  hasPySerial = True
except:
  hasPySerial = False
import threading
import struct
import time
import barobo

DEBUG=False

class Packet:
  def __init__(self, data=None, addr=None):
    self.data = data
    self.addr = addr

  def __getitem__(self, key):
    return self.data[key]

  def __len__(self):
    return len(self.data)

if hasPySerial:
  class PhysicalLayer_TTY(serial.Serial):
    def __init__(self, ttyfilename):
      serial.Serial.__init__(self, ttyfilename, baudrate=230400)
      time.sleep(1)
      self.stopbits = serial.STOPBITS_TWO
      self.timeout = None

    def disconnect(self):
      pass

class PhysicalLayer_Socket(socket.socket):
  def __init__(self, hostname, port):
    socket.socket.__init__(self)
    self.connect((hostname, port))

  def disconnect(self):
    self.close()

  def flush(self):
    pass
  def flushInput(self):
    pass
  def flushOutput(self):
    pass

  def read(self):
    # Read and return a single byte
    return self.recv(1)

  def write(self, packet):
    self.sendall(packet)

import sys
if sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
  # We can use sockets for Bluetooth
  import socket
  class PhysicalLayer_Bluetooth():
    def __init__(self, bluetooth_mac_addr):
      self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
      self.sock.connect((bluetooth_mac_addr, 1))

    def disconnect(self):
      self.sock.close()

    def flush(self):
      pass
    def flushInput(self):
      pass
    def flushOutput(self):
      pass
    def read(self):
      return self.sock.recv(1)
    def write(self, packet):
      self.sock.sendall(packet)

else:
  try:
    import bluetooth
    class PhysicalLayer_Bluetooth(bluetooth.BluetoothSocket):
      def __init__(self, bluetooth_mac_addr):
        bluetooth.BluetoothSocket.__init__(self, bluetooth.RFCOMM)
        self.connect((bluetooth_mac_addr, 1))

      def disconnect(self):
        self.close()

      def flush(self):
        pass
      def flushInput(self):
        pass
      def flushOutput(self):
        pass

      def read(self):
        return self.recv(1)

      def write(self, packet):
        import os
        if os.name == 'nt':
          self.send(str(packet))
        else:
          self.sendall(str(packet))
  except:
    pass

class LinkLayer_Base:
  def __init__(self, physicalLayer, readCallback):
    self.phys = physicalLayer
    self.deliver = readCallback
    self.writeLock = threading.Lock()

  def start(self):
    self.thread = threading.Thread(target=self._run)
    self.thread.daemon = True
    self.thread.start()

class LinkLayer_TTY(LinkLayer_Base):
  def __init__(self, physicalLayer, readCallback):
    LinkLayer_Base.__init__(self, physicalLayer, readCallback)

  def write(self, packet, address):
    newpacket = bytearray([ packet[0],
                            len(packet)+5,
                            address>>8,
                            address&0x00ff,
                            1 ])
    newpacket += bytearray(packet)
    self.writeLock.acquire()
    if DEBUG:
      print ("Send: {0}".format(list(map(hex, newpacket))))
    self.phys.write(newpacket)
    self.writeLock.release()

  def _run(self):
    # Try to read byte from physical layer
    self.readbuf = bytearray([])
    self.phys.flush()
    self.phys.flushInput()
    self.phys.flushOutput()
    while True:
      byte = self.phys.read()
      if byte is None:
        continue
      if DEBUG:
        print ("Byte: {0}".format(list(map(hex, bytearray(byte)))))
      self.readbuf += bytearray(byte)
      if (len(self.readbuf) <= 2):
        continue
      if len(self.readbuf) == self.readbuf[1]:
        # Received whole packet
        if DEBUG:
          print ("Recv: {0}".format(list(map(hex, self.readbuf))))
        zigbeeAddr = barobo._unpack('!H', self.readbuf[2:4])[0]
        if self.readbuf[0] != barobo.BaroboCtx.EVENT_REPORTADDRESS:
          pkt = Packet(self.readbuf[5:-1], zigbeeAddr)
        else:
          pkt = Packet(self.readbuf, zigbeeAddr)
        self.deliver(pkt)
        self.readbuf = self.readbuf[self.readbuf[1]:]

class LinkLayer_Socket(LinkLayer_Base):
  def __init__(self, physicalLayer, readCallback):
    LinkLayer_Base.__init__(self, physicalLayer, readCallback)

  def write(self, packet, address):
    self.writeLock.acquire()
    if DEBUG:
      print ("Send: {0}".format(list(map(hex, packet))))
    self.phys.write(packet)
    self.writeLock.release()

  def _run(self):
    # Try to read byte from physical layer
    self.readbuf = bytearray([])
    self.phys.flush()
    self.phys.flushInput()
    self.phys.flushOutput()
    while True:
      byte = self.phys.read()
      if DEBUG:
        print ("Byte: {0}".format(list(map(hex, bytearray(byte)))))
      if byte is None:
        continue
      self.readbuf += bytearray(byte)
      if (len(self.readbuf) <= 2):
        continue
      if len(self.readbuf) == self.readbuf[1]:
        # Received whole packet
        if DEBUG:
          print ("Recv: {0}".format(list(map(hex, self.readbuf))))
        pkt = Packet(self.readbuf, 0x8000)
        self.deliver(pkt)
        self.readbuf = self.readbuf[self.readbuf[1]:]


