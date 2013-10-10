#!/usr/bin/env python

import threading
import time
import struct
try:
  import Queue
except:
  import queue as Queue

import barobo
import barobo._comms as _comms
import barobo._util as _util

class Linkbot:
  """
  The Linkbot Class
  =================

  Each instance of this class can be used to represent a physical Linkbot. The
  member functions of this class can be used to get data, set motor angles,
  beep the buzzer, scan for button events, and more.  

  Blocking and Non-Blocking Member Functions
  ==========================================

  The member functions of the Linkbot class which are responsible for moving
  the joints of the Linkbot can be categorized into two general types of
  functions; "blocking" functions and "non-blocking" functions. A blocking
  function is a function that "hangs" until the complete motion is done,
  whereas a "non-blocking" function returns as soon as the motion begins,
  but does not wait until it is done. In the Linkbot class, all functions
  are blocking unless the have the suffix "NB", such as "Linkbot.moveNB()".

  For example, consider the following lines of code::
    linkbot.move(360, 0, 0)
    linkbot.setBuzzerFrequency(440)
  When the above lines of code are executed, the Linkbot will rotate joint 1
  360 degrees. Once the joint has rotated the full revolution, the buzzer will
  sound. Now consider the following code::
    linkbot.moveNB(360, 0, 0)
    linkbot.setBuzzerFrequency(440)
  For these lines of code, joint 1 also moves 360 degrees. The difference is 
  that with these lines of code, the buzzer will begin emitting a tone as soon
  as the joint begins turning, instead of waiting for the motion to finish.
  This is because the non-blocking version of move() was used, which returns
  immediately after the joint begins moving allowing the setBuzzerFrequency() 
  function to execute as the joint begins moving.

  The L{moveWait()<barobo.linkbot.Linkbot.moveWait>} function can be used to block until non-blocking motion 
  functions are finished. For instance, the following two blocks of code
  will accomplish the same task::
    linkbot.move(360, 0, 0)
    linkbot.setBuzzerFrequency(440)

    linkbot.moveNB(360, 0, 0)
    linkbot.moveWait()
    linkbot.setBuzzerFrequency(440)

  """

  def __init__(self):
    self.responseQueue = Queue.Queue()
    self.eventQueue = Queue.Queue()
    self.readQueue = Queue.Queue()
    self.writeQueue = Queue.Queue()
    self.zigbeeAddr = None
    self.serialID = None
    self.baroboCtx = None
    self.messageThread = threading.Thread(target=self.__messageThread)
    self.messageThread.daemon = True
    self.messageThread.start()
    self.messageLock = threading.Lock()
    self.eventThread = threading.Thread(target=self.__eventThread)
    self.eventThread.daemon = True
    self.eventThread.start()

    self.callbackEnabled = False

  def checkStatus(self):
    """
    Check to see if the Linkbot is online. Raises an exception if the Linkbot
    is not online.
    """
    buf = bytearray([barobo.BaroboCtx.CMD_STATUS, 3, 0])
    self.__transactMessage(buf)

  def connect(self):
    """
    Connect to a Linkbot through BaroboLink
    """
    # Connect to a running instance of BaroboLink
    # First, make sure we have a BaroboCtx
    self.zigbeeAddr = 0x8000
    if not self.baroboCtx:
      self.baroboCtx = barobo.BaroboCtx()
      self.baroboCtx.connect()
      self.baroboCtx.addLinkbot(self)
    self.getSerialID()
    self.form = self.getFormFactor()

  def connectBluetooth(self, bluetooth_mac_addr):
    """
    Connect to a bluetooth enabled Linkbot.

    @type bluetooth_mac_addr: string
    @param bluetooth_mac_addr: The MAC address of the bluetooth Linkbot. Should
      be something like '00:06:66:6D:12:34'
    """
    self.zigbeeAddr = 0x0000
    if not self.baroboCtx:
      self.baroboCtx = barobo.BaroboCtx()
      self.baroboCtx.connectBluetooth(bluetooth_mac_addr)
      self.baroboCtx.addLinkbot(self)
      self.zigbeeAddr = self.baroboCtx.zigbeeAddr
    self.checkStatus()
    self.getSerialID()
    self.form = self.getFormFactor()

  def disableButtonCallback(self):
    """
    Disable the button callback.

    See also: enableButtonCallback()
    """
    self.callbackEnabled = False
    buf = bytearray([barobo.BaroboCtx.CMD_ENABLEBUTTONHANDLER, 0x04, 0x00, 0x00])
    self.__transactMessage(buf)

  def disconnect(self):
    """
    Disconnect from the Linkbot.
    """
    buf = bytearray([barobo.BaroboCtx.CMD_UNPAIRPARENT, 3, 0])
    response = self.__transactMessage(buf)
    self.baroboCtx.disconnect()
    self.baroboCtx = None

  def driveJointTo(self, joint, angle):
    """
    Drive a single joint to a position as fast as possible, using the on-board
    PID motor controller.

    @type joint: number [1,3]
    @param joint: The joint to move
    @type angle: number
    @param angle: The angle to move the joint to, in degrees
    """
    self.driveJointToNB(joint, angle)
    self.moveWait()

  def driveJointToNB(self, joint, angle):
    """
    Non-blocking version of driveJointTo(). Please see driveJointTo() for more
    details.
    """
    angle = _util.deg2rad(angle)
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORANGLEPID, 0x08, joint-1])
    buf += bytearray(struct.pack('<f', angle))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def driveTo(self, angle1, angle2, angle3):
    """
    Drive the joints to angles as fast as possible using on-board PID
    controller.

    @type angle1: number
    @param angle1: Position to move the joint, in degrees
    @type angle2: number
    @param angle2: Position to move the joint, in degrees
    @type angle3: number
    @param angle3: Position to move the joint, in degrees
    """
    self.driveToNB(angle1, angle2, angle3)
    self.moveWait()

  def driveToNB(self, angle1, angle2, angle3):
    """
    Non-blocking version of driveTo(). See driveTo() for more details
    """
    angle1 = _util.deg2rad(angle1)
    angle2 = _util.deg2rad(angle2)
    angle3 = _util.deg2rad(angle3)
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORANGLESPID, 0x13])
    buf += bytearray(struct.pack('<4f', angle1, angle2, angle3, 0.0))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def enableButtonCallback(self, callbackfunc, userdata=None):
    """
    Enable button callbacks. This function temporarily disables the
    robot's default button actions. Instead, whenever a button is
    pressed or released, the function given as the parameter 'callbackfunc'
    is called.

    See also: disableButtonCallback()

    @type userdata: Anything
    @param userdata: This is data that will be passed into the callbackfunc
      whenever it is called.
    @type callbackfunc: function: func(buttonMask, buttonDown, userdata) . The 
      'buttonMask' parameter of the callback function will contain a bitmask
      indicating which buttons have changed. The buttonDown parameter
      is another bitmask, indicating the current state of each button.
    """
    self.callbackfunc = callbackfunc
    self.callbackUserData = userdata
    self.callbackEnabled = True  
    buf = bytearray([barobo.BaroboCtx.CMD_ENABLEBUTTONHANDLER, 0x04, 0x01, 0x00])
    self.__transactMessage(buf)

  def _getADCVolts(self, adc):
    buf = bytearray([barobo.BaroboCtx.CMD_GETENCODERVOLTAGE, 4, adc, 0])
    response = self.__transactMessage(buf)
    voltage = barobo._unpack('<f', response[2:6])[0]
    return voltage

  def getAccelerometerData(self):
    """
    Get the current accelerometer readings

    @rtype: [number, number, number]
    @return: A list of acceleration values in the x, y, and z directions.
      Accelerometer values are in units of "G's", where 1 G is standard earth
      gravitational acceleration (9.8m/s/s)
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETACCEL, 0x03, 0x00])
    response = self.__transactMessage(buf)
    values = barobo._unpack('<3h', response[2:8])
    return list(map(lambda x: x/16384.0, values))

  def getBatteryVoltage(self):
    """
    Get the current battery voltage of the Linkbot.

    @rtype: number
    @return: Returns a value in Volts
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETBATTERYVOLTAGE, 0x03, 0x00])
    response = self.__transactMessage(buf)
    voltage = barobo._unpack('<f', response[2:6])[0]
    return voltage

  def getBreakoutADC(self, adc):
    """
    Get the ADC (Analog-to-digital) reading from a breakout-board's ADC
    channel. 

    @type adc: number
    @param adc: The ADC channel to get the value from [0, 7]
    @rtype: number
    @return: Value from 0-1023
    """
    buf = bytearray([barobo.BaroboCtx.TWIMSG_HEADER, barobo.BaroboCtx.TWIMSG_ANALOGREADPIN, adc])
    data = self.twiSendRecv(0x02, buf, 2)
    return barobo._unpack('!h', data)[0]

  def getBreakoutADCVolts(self, adc):
    """
    Get the voltage reading of an ADC pin.

    Note that the voltage is calibrated using the AVCC reference. If the
    reference is changed using the setBreakoutADCReference() function, the
    values reported by this function may no longer be accurate.

    @type adc: number
    @param adc: The ADC channel to get the value from [0, 7]
    @rtype: number
    @return: Floating point voltage from 0 to 5
    """
    return self.getBreakoutADC(adc)/1024.0 * 5

  def getBreakoutDigitalPin(self, pin):
    """
    Read value from digital I/O pin.

    @rtype: integer
    @return: Returns 0 if pin is grounded, or 1 in pin is high.
    """
    buf = bytearray([barobo.BaroboCtx.TWIMSG_HEADER, barobo.BaroboCtx.TWIMSG_DIGITALREADPIN, pin])
    data = self.twiSendRecv(0x02, buf, 1)
    return data[0]
    
  def getColorRGB(self):
    """
    Get the current RGB values of the rgbled

    @rtype: [number, number, number]
    @return: The red, green, and blue values from 0 to 255
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETRGB, 0x03, 0x00])
    response = self.__transactMessage(buf)
    return barobo._unpack('<3B', response[2:5])

  def getFormFactor(self):
    """
    Get the form factor.

    @rtype: Robot Form
    @return: Returns barobo.ROBOTFORM_MOBOT, barobo.ROBOTFORM_I, 
      barobo.ROBOTFORM_L, or barobo.ROBOTFORM_T
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETFORMFACTOR, 0x03, 0x00])
    response = self.__transactMessage(buf)
    return response[2] 

  def getJointAngle(self, joint):
    """
    Get the current angle position of a joint.

    @type joint: number
    @param joint: Get the position of this joint. Can be 1, 2, or 3
    @rtype: number
    @return: Return the joint angle in degrees
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETMOTORANGLE, 0x04, joint-1, 0x00])
    response = self.__transactMessage(buf)
    return _util.rad2deg(barobo._unpack('<f', response[2:6])[0])

  def getJointAngles(self):
    """
    Get the current joint angles.

    @rtype: [float, float, float]
    @return: The joint angles in degrees
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETMOTORANGLESABS, 3, 0])
    response = self.__transactMessage(buf)
    angles = barobo._unpack('<4f', response[2:18])
    return list(map(_util.rad2deg, angles[:3]))

  def getJointAnglesTime(self):
    """
    Get the joint angles with a timestamp. The timestamp is the number of
    seconds since the robot has powered on.

    @rtype: [numbers]
    @return: [seconds, angle1, angle2, angle3], all angles in degrees
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETMOTORANGLESTIMESTAMPABS, 0x03, 0x00])
    response = self.__transactMessage(buf)
    millis = barobo._unpack('<L', response[2:6])[0]
    data = barobo._unpack('<4f', response[6:-1])
    rc = [millis/1000.0]
    rc += list(map(_util.rad2deg, data[:3]))
    return rc

  def getLinkbot(self, addr):
    """
    Use an instance of a Linkbot to get instances to other Linkbots. Note that
    this only works for Linkbots that are connected via Bluetooth or TTY, but
    does not work for Linkbots that are connected to BaroboLink.
    """
    return self.baroboCtx.getLinkbot(addr)

  def getSerialID(self):
    """
    Get the serial ID from the Linkbot

    @return: A four character string
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETSERIALID, 3, 0])
    response = self.__transactMessage(buf) 
    botid = barobo._unpack('!4s', response[2:6])[0]
    self.serialID = botid
    return botid

  def getVersion(self):
    """
    Get the firmware version of the Linkbot
    """
    buf = bytearray([barobo.BaroboCtx.CMD_GETVERSION, 3, 0])
    response = self.__transactMessage(buf)
    return response[2]

  def isMoving(self):
    buf = bytearray([barobo.BaroboCtx.CMD_IS_MOVING, 3, 0])
    response = self.__transactMessage(buf)
    return response[2]

  def moveJoint(self, joint, angle):
    """
    Move a joint from it's current position by 'angle' degrees.

    @type joint: number
    @param joint: The joint to move: 1, 2, or 3
    @type angle: number
    @param angle: The number of degrees to move the joint from it's current
      position. For example, "45" will move the joint in the positive direction
      by 45 degrees from it's current location, and "-30" will move the joint
      in the negative direction by 30 degrees.
    """
    curangle = self.getJointAngle(joint)
    self.moveJointTo(joint, curangle + angle)

  def moveJointNB(self, joint, angle):
    """
    Non-blocking version of moveJoint(). See moveJoint() for more details.
    """
    curangle = self.getJointAngle(joint)
    self.moveJointToNB(joint, curangle + angle)

  def moveJointTo(self, joint, angle):
    """
    Move a joint to an angle.

    @type joint: number
    @param joint: The joint to move: 1, 2, or 3
    @type angle: number
    @param angle: The absolute position you want the joint to move to. Values are
      in degrees and can be any value. For example, the value "720" means two full
      rotations in the positive directions past "0".
    """
    self.moveJointToNB(joint, angle)
    self.moveWait()

  def moveJointToNB(self, joint, angle):
    """
    Non-blocking version of moveJointTo. See moveJointTo for more details.
    """
    angle = _util.deg2rad(angle)
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORANGLEABS, 0x08, joint-1])
    buf += bytearray(struct.pack('<f', angle))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def move(self, angle1, angle2, angle3):
    """
    Move all of the joints on a robot by a number of degrees.

    @type angle1: number
    @param angle1: Number of degrees to move joint 1. Similar for parameters
      'angle2' and 'angle3'.
    """
    self.moveNB(angle1, angle2, angle3)
    self.moveWait()

  def moveNB(self, angle1, angle2, angle3):
    """
    Non-blocking version of move(). See move() for more details
    """
    angles = self.getJointAngles()
    self.moveToNB(angle1+angles[0], angle2+angles[1], angle3+angles[2])

  def moveContinuous(self, dir1, dir2, dir3):
    """
    Make the joints begin moving continuously.

    @type dir1: Barobo Direction Macro
    @param dir1: This parameter may take the following values:
      - ROBOT_NEUTRAL: Makes the joint relax
      - ROBOT_FORWARD: Rotates the joint to move the robot in the "forward"
        direction, if the robot has wheels.
      - ROBOT_BACKWARD: Same as above but backwards
      - ROBOT_HOLD: Hold the joint at its current position
      - ROBOT_POSITIVE: Rotates the joint in the "positive" direction,
        according to the right-hand-rule.
      - ROBOT_NEGATIVE: Same as above but in the negative direction.
    """
    self.setMovementState(dir1, dir2, dir3)

  def moveTo(self, angle1, angle2, angle3):
    self.moveToNB(angle1, angle2, angle3)
    self.moveWait()

  def moveToNB(self, angle1, angle2, angle3):
    """
    Move all joints on the Linkbot. Linkbot-I modules will ignore the 'angle2'
    parameter and Linkbot-L modules will ignore the 'angle3' parmeter.

    This function is the non-blocking version of moveTo(), meaning this
    function will return immediately after the robot has begun moving and will
    not wait until the motion is finished.

    @type angle1: number
    @param angle1: Position to move the joint, in degrees
    @type angle2: number
    @param angle2: Position to move the joint, in degrees
    @type angle3: number
    @param angle3: Position to move the joint, in degrees
    """
    angle1 = _util.deg2rad(angle1)
    angle2 = _util.deg2rad(angle2)
    angle3 = _util.deg2rad(angle3)
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORANGLESABS, 0x13])
    buf += bytearray(struct.pack('<4f', angle1, angle2, angle3, 0.0))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def moveWait(self):
    """
    Wait until the current robotic motion is finished.
    """
    while self.isMoving():
      time.sleep(0.1)

  def _pairParent(self):
    buf = bytearray([barobo.BaroboCtx.CMD_PAIRPARENT, 5])
    buf += bytearray(struct.pack('!H', self.baroboCtx.zigbeeAddr))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def ping(self, numbytes=4):
    import random
    now = time.time()
    buf = bytearray([barobo.BaroboCtx.CMD_PING, 0])
    randbytes = bytearray([random.randint(0, 255) for _ in range(numbytes)])
    buf += randbytes
    buf += bytearray([0x00])
    buf[1] = len(buf)
    response = self.__transactMessage(buf, maxTries = 1, timeout = 0.5)
    if response[2:-1] != randbytes:
      raise barobo.BaroboException('Ping did not receive correct bytes.')
    return time.time() - now

  def reboot(self):
    """
    Reboot the connect robot. Note that communications with the robot will 
    not succeed while the robot is booting back up.
    """
    buf = bytearray([barobo.BaroboCtx.CMD_REBOOT, 0x03, 0x00])
    self.__transactMessage(buf)

  def recordAnglesBegin(self, delay=0.05):
    """
    Begin recording joint angles.

    @type delay: number
    @param delay: The number of seconds to delay between joint angles readings.
    """
    self.recordThread = _LinkbotRecordThread(self, delay)
    self.recordThread.start()

  def recordAnglesEnd(self):
    """ End recording angles and return a list consisting of [time_values,
    joint1angles, joint2angles, joint3angles]"""
    self.recordThread.runflag_lock.acquire()
    self.recordThread.runflag = False
    self.recordThread.runflag_lock.release()
    # Wait for recording to end
    while self.recordThread.isRunning:
      time.sleep(0.5)
    return [map(lambda x: x-self.recordThread.time[0], self.recordThread.time), 
        self.recordThread.angles[0], 
        self.recordThread.angles[1], 
        self.recordThread.angles[2]]

  def recordAnglesPlot(self):
    import pylab
    """Plot recorded angles.

    See recordAnglesBegin() and recordAnglesEnd() to record joint motions.
    """
    pylab.plot(
        self.recordThread.time, 
        self.recordThread.angles[0],
        self.recordThread.time, 
        self.recordThread.angles[1],
        self.recordThread.time, 
        self.recordThread.angles[2])
    pylab.show()

  def reset(self):
    """
    Reset the multi-revolution counter on the joints.
    """
    buf = bytearray([barobo.BaroboCtx.CMD_RESETABSCOUNTER, 0x03, 0x00])
    self.__transactMessage(buf)

  def resetToZero(self):
    """
    Reset the multi-revolution counter and move all the joints to zero
    positions.
    """
    self.reset()
    self.moveTo(0, 0, 0)

  def resetToZeroNB(self):
    self.reset()
    self.moveToZeroNB()

  def setAcceleration(self, accel):
    """
    Set the acceleration of all joints. Each joint motion will begin with this
    acceleration after calling this function. Set the acceleration to 0 to
    disable this feature. 
    """
    buf = bytearray([barobo.BaroboCtx.CMD_SETGLOBALACCEL, 0])
    buf += struct.pack('<f', _util.deg2rad(accel))
    buf += bytearray([0x00])
    buf[1] = len(buf)
    self.__transactMessage(buf)

  def setBreakoutAnalogPin(self, pin, value):
    """
    Set an analog output pin (PWM) to a value between 0-255. This can be used
    to set the power of a motor, dim a LED, or more. 

    @type pin: integer from 0-7
    @param pin: The pin parameter must be a pin the supports analog output. 
      These pins are indicated by a tilde (~) symbol next to the pin number
      printed on the breakout board.
    @type value: integer from 0-255
    @param value: The amount to power the pin: 0 is equivalent to no power, 255
      is maximum power.
    """
    buf = bytearray([barobo.BaroboCtx.TWIMSG_HEADER, barobo.BaroboCtx.TWIMSG_ANALOGWRITEPIN, pin, value])
    self.twiSend(0x02, buf)

  def setBreakoutAnalogRef(self, pin, ref):
    """
    Set the reference voltage of an analog input pin. 

    @type pin: integer from 0-7
    @param ref: Valid values are barobo.AREF_DEFAULT, barobo.AREF_INTERNAL,
      barobo.AREF_INTERNAL1V1, barobo.AREF_INTERNAL2V56, and
      barobo.AREF_EXTERNAL.
    """
    buf = bytearray([barobo.BaroboCtx.TWIMSG_HEADER, barobo.BaroboCtx.TWIMSG_ANALOGREF, pin, ref])
    self.twiSend(0x02, buf)

  def setBreakoutDigitalPin(self, pin, value):
    """
    Set a digital I/O pin to either a high or low value. The pin will be set
    high if the parameter 'value' is non-zero, or set to ground otherwise.
    """
    buf = bytearray([barobo.BaroboCtx.TWIMSG_HEADER, barobo.BaroboCtx.TWIMSG_DIGITALWRITEPIN, pin, value])
    self.twiSend(0x02, buf)

  def setBreakoutPinMode(self, pin, mode):
    """
    Set the mode of a digital I/O pin on the breakout board. Valid modes are
    barobo.PINMODE_INPUT, barobo.PINMODE_OUTPUT, and
    barobo.PINMODE_INPUTPULLUP.
    """
    buf = bytearray([barobo.BaroboCtx.TWIMSG_HEADER, barobo.BaroboCtx.TWIMSG_SETPINMODE, pin, mode])
    self.twiSend(0x02, buf)

  def setBuzzerFrequency(self, freq):
    """
    Set the buzzer to begin playing a tone.

    @type freq: number in Hz
    @param freq: The frequency in Hertz (Hz) for the buzzer to play. Set to
      zero to turn the buzzer off.
    """
    buf = bytearray([0x6A, 0x05, (freq>>8)&0xff, freq&0xff, 0x00])
    self.__transactMessage(buf)

  def setJointMovementState(self, joint, state):
    """
    Set a joint movement state

    @type state: Barobo Direction Macro
    @param state: This parameter may take the following values:
      - ROBOT_NEUTRAL: Makes the joint relax
      - ROBOT_FORWARD: Rotates the joint to move the robot in the "forward"
        direction, if the robot has wheels.
      - ROBOT_BACKWARD: Same as above but backwards
      - ROBOT_HOLD: Hold the joint at its current position
      - ROBOT_POSITIVE: Rotates the joint in the "positive" direction,
        according to the right-hand-rule.
      - ROBOT_NEGATIVE: Same as above but in the negative direction.
    """
    if (self.form == ROBOTFORM_I) and (joint==3):
      if state == ROBOT_FORWARD:
        state = ROBOT_BACKWARD
      elif state == ROBOT_BACKWARD:
        state = ROBOT_FORWARD
      elif state == ROBOT_POSITIVE:
        state = ROBOT_FORWARD
      elif state == ROBOT_NEGATIVE:
        state = ROBOT_BACKWARD
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORDIR, 0x05, joint-1, state, 0x00])
    self.__transactMessage(buf)

  def setJointSpeed(self, joint, speed):
    """
    Set the speed of a joint.

    @type joint: number
    @param joint: The joint to change the speed. Can be 1, 2, or 3
    @type speed: number
    @param speed: The speed to set the joint to, in degrees/second.
    """
    _speed = _util.deg2rad(speed)
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORSPEED, 0x08, joint-1])
    buf += bytearray(struct.pack('<f', _speed))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def setJointSpeeds(self, speed1, speed2, speed3):
    """
    Set all three motor speed simultaneously. Parameters in degrees/second.
    """
    self.setJointSpeed(1, speed1)
    self.setJointSpeed(2, speed2)
    self.setJointSpeed(3, speed3)
    
  def setJointState(self, joint, state):
    """
    Set a joint's movement state.

    @param joint: The joint id: 1, 2, or 3
    @type state: Barobo Direction Macro
    @param state: This parameter may take the following values:
      - ROBOT_NEUTRAL: Makes the joint relax
      - ROBOT_FORWARD: Rotates the joint to move the robot in the "forward"
        direction, if the robot has wheels.
      - ROBOT_BACKWARD: Same as above but backwards
      - ROBOT_HOLD: Hold the joint at its current position
      - ROBOT_POSITIVE: Rotates the joint in the "positive" direction,
        according to the right-hand-rule.
      - ROBOT_NEGATIVE: Same as above but in the negative direction.
    """
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORDIR, 5, joint-1, state, 0])
    self.__transactMessage(buf)

  def setJointStates(self, states, speeds):
    """
    Set the joint states for all 3 joints simultaneously.

    @type states: [state1, state2...]
    @param states: Each state may take the following values:
      - ROBOT_NEUTRAL: Makes the joint relax
      - ROBOT_FORWARD: Rotates the joint to move the robot in the "forward"
        direction, if the robot has wheels.
      - ROBOT_BACKWARD: Same as above but backwards
      - ROBOT_HOLD: Hold the joint at its current position
      - ROBOT_POSITIVE: Rotates the joint in the "positive" direction,
        according to the right-hand-rule.
      - ROBOT_NEGATIVE: Same as above but in the negative direction.
    @type speeds: [speed1, speed2 ...]
    @param speeds: The speeds to set each joint

    """
    if len(states) < 4:
      states += [0]*(4-len(states))
    if len(speeds) < 4:
      speeds += [0.0]*(4-len(speeds))
    speeds = list(map(_util.deg2rad, speeds))
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORSTATES, 23])
    buf += bytearray(states)
    buf += bytearray(struct.pack('<4f', speeds[0], speeds[1], speeds[2], speeds[3]))
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def setLEDColor(self, r, g, b):
    """
    Set the LED color

    @type r: number [0, 255]
    @type g: number [0, 255]
    @type b: number [0, 255]
    """

    buf = bytearray([barobo.BaroboCtx.CMD_RGBLED, 8, 0xff, 0xff, 0xff, r, g, b, 0x00])
    self.__transactMessage(buf)

  def setMotorPower(self, joint, power):
    """
    Set the power of a motor.

    @type joint: number
    @param joint: The joint to control. Can be 1, 2, or 3
    @type power: integer
    @param power: An integer between -255 and 255.
    """
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORPOWER, 0x0A, 1<<joint])
    buf +=bytearray(struct.pack('>3h', power, power, power))
    buf +=bytearray([0x00])
    self.__transactMessage(buf)

  def setMotorPowers(self, power1, power2, power3):
    buf = bytearray([barobo.BaroboCtx.CMD_SETMOTORPOWER, 0x0A, 0x07])
    buf +=bytearray(struct.pack('>3h', power1, power2, power3))
    buf +=bytearray([0x00])
    self.__transactMessage(buf)

  def setMovementState(self, state1, state2, state3):
    """
    Set the movement state for all three motors.

    @type state1: movement_state
    @param state1: This parameter may take the following values:
      - ROBOT_NEUTRAL: Makes the joint relax
      - ROBOT_FORWARD: Rotates the joint to move the robot in the "forward"
        direction, if the robot has wheels.
      - ROBOT_BACKWARD: Same as above but backwards
      - ROBOT_HOLD: Hold the joint at its current position
      - ROBOT_POSITIVE: Rotates the joint in the "positive" direction,
        according to the right-hand-rule.
      - ROBOT_NEGATIVE: Same as above but in the negative direction.
    """
    if self.form == barobo.ROBOTFORM_I:
      if state3 == barobo.ROBOT_FORWARD:
        state3 = barobo.ROBOT_BACKWARD
      elif state3 == barobo.ROBOT_BACKWARD:
        state3 = barobo.ROBOT_FORWARD
      elif state3 == barobo.ROBOT_POSITIVE:
        state3 = barobo.ROBOT_FORWARD
      elif state3 == barobo.ROBOT_NEGATIVE:
        state3 = barobo.ROBOT_BACKWARD
    states = [state1, state2, state3, 0]
    buf = bytearray([barobo.BaroboCtx.CMD_TIMEDACTION, 0, 0x07])
    for state in states:
      buf += bytearray([state1, barobo.ROBOT_HOLD])
      buf += bytearray(struct.pack('<i', -1))
    buf += bytearray([0x00])
    buf[1] = len(buf)
    self.__transactMessage(buf)

  def smoothMoveTo(self, joint, accel0, accelf, vmax, angle):
    """
    Move a joint to a desired position with a specified amount of starting and
    stopping acceleration.

    @type joint: number
    @param joint: The joint to move
    @type accel0: number
    @param accel0: The starting acceleration, in deg/sec/sec
    @type accelf: number
    @param accelf: The stopping deceleration, in deg/sec/sec
    @type vmax: number
    @param vmax: The maximum velocity for the joint during the motion, in deg/sec
    @type angle: number
    @param angle: The absolute angle to move the joint to, in degrees
    """
    _accel0 = _util.deg2rad(accel0)
    _accelf = _util.deg2rad(accelf)
    _vmax = _util.deg2rad(vmax)
    _angle = _util.deg2rad(angle)
    buf = bytearray([barobo.BaroboCtx.CMD_SMOOTHMOVE, 20, joint-1])
    buf += bytearray(struct.pack('<4f', _accel0, _accelf, _vmax, _angle))
    buf += bytearray([0x00])
    buf[1] = len(buf)
    self.__transactMessage(buf)

  def stop(self):
    buf = bytearray([barobo.BaroboCtx.CMD_STOP, 0x03, 0x00])
    self.__transactMessage(buf)

  def twiRecv(self, addr, size):
    """
    Receive data from a TWI device. See twiSend() for more details.

    @param addr: The TWI address to send data to.
    @rtype: bytearray
    """
    twibuf = bytearray(data)
    buf = bytearray([barobo.BaroboCtx.CMD_TWI_SEND, len(data)+5, addr, len(data)])
    buf += bytearray(data)
    buf += bytearray([0x00])
    response = self.__transactMessage(buf)
    return bytearray(response[2:-1])
   
  def twiSend(self, addr, data):
    """ 
    Send data onto the Two-Wire Interface (TWI) (aka I2c) of the Linkbot.
    Many Linkbot peripherals are located on the TWI bus, including the
    accelerometer, breakout boards, and some sensors. The black phone-jack on
    top of the Linkbot exposes TWI pins where custom or prebuild peripherals
    may be attached.

    @param addr: The TWI address to send data to.
    @type data: iterable bytes
    @param data: The byte data to send to the peripheral
    """
    twibuf = bytearray(data)
    buf = bytearray([barobo.BaroboCtx.CMD_TWI_SEND, len(twibuf)+5, addr, len(twibuf)])
    buf += twibuf
    buf += bytearray([0x00])
    self.__transactMessage(buf)

  def twiSendRecv(self, addr, senddata, recvsize):
    """
    Send and receive data from a TWI device attached to the Linkbot. See
    twiSend() and twiRecv() for more details.

    @param addr: The TWI address to send data to.
    @type senddata: iterable
    @param senddata: The byte data to send to the peripheral
    @type recvsize: number
    @param recvsize: Number of bytes expected from TWI device
    @rtype: bytearray
    """
    twibuf = bytearray(senddata)
    buf = bytearray([barobo.BaroboCtx.CMD_TWI_SENDRECV, 0, addr, len(twibuf)])
    buf += twibuf
    buf += bytearray([recvsize, 0x00])
    buf[1] = len(buf)
    response = self.__transactMessage(buf)
    return bytearray(response[2:-1])

  def __transactMessage(self, buf, maxTries = 3, timeout = 2.0):
    self.messageLock.acquire()
    numTries = 0
    while numTries < maxTries:
      try:
        self.baroboCtx.writePacket(_comms.Packet(buf, self.zigbeeAddr))
        response = self.responseQueue.get(block=True, timeout = timeout)
        break
      except:
        if numTries < maxTries:
          numTries+=1
          continue
        else:
          self.messageLock.release()
          raise barobo.BaroboException('Did not receive response from robot.')
    if response[0] != barobo.BaroboCtx.RESP_OK:
      self.messageLock.release()
      raise barobo.BaroboException('Robot returned error status.')
    self.messageLock.release()
    return response

  def __messageThread(self):
    # Scan and act on incoming messages
    while True:
      pkt = self.readQueue.get(block=True, timeout=None)
      if (pkt[0] == barobo.BaroboCtx.RESP_OK) or \
         (pkt[0] == barobo.BaroboCtx.RESP_ERR) or \
         (pkt[0] == barobo.BaroboCtx.RESP_ALREADY_PAIRED):
        self.responseQueue.put(pkt)
      else:
        self.eventQueue.put(pkt)

  def __eventThread(self):
    while True:
      evt = self.eventQueue.get(block=True, timeout=None)
      if (evt[0] == barobo.BaroboCtx.EVENT_BUTTON) and self.callbackEnabled:
        self.callbackfunc(evt[6], evt[7], self.callbackUserData)
      elif evt[0] == barobo.BaroboCtx.EVENT_DEBUG_MSG:
        s = barobo._unpack(s, evt[2:-1])
        print ("Debug msg from {0}: {1}".format(self.serialID, s))

class _LinkbotRecordThread(threading.Thread):
  def __init__(self, linkbot, delay):
    self.delay = delay
    self.linkbot = linkbot
    self.runflag = False
    self.isRunning = False;
    self.runflag_lock = threading.Lock()
    self.time = []
    self.angles = [ [], [], [] ]
    threading.Thread.__init__(self)
    self.daemon = True

  def run(self):
    self.runflag = True
    self.isRunning = True
    while True:
      self.runflag_lock.acquire()
      if self.runflag == False:
        self.runflag_lock.release()
        break
      self.runflag_lock.release()
      # Get the joint angles and stick them into our data struct
      try:
        numtries = 0
        data = self.linkbot.getJointAnglesTime()
        self.time.append(data[0])
        self.angles[0].append(data[1])
        self.angles[1].append(data[2])
        self.angles[2].append(data[3])
        time.sleep(self.delay)
      except IOError:
        numtries += 1
        if numtries >= 3:
          raise
          break
        continue
    self.isRunning = False
