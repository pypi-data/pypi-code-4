# Copyright Abel Deuring 2012, 2013
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

__metaclass__ = type

import logging
import re
import sys
from textwrap import dedent
from time import sleep, time
from types import MethodType

from ptp import (
    CHDKMessageType,
    CHDKScriptStatus,
    PTPDevice,
    )


_MESSAGE_WAIT_DELAY = 0.01
_DEFAULT_MESSAGE_TIMEOUT = 5


class LuaError(Exception):
    """Raised when the camera script returns an error."""


class PTPControllerError(Exception):
    """Raised when PTPController methods detect an error."""


class StuckMessage(Exception):
    """Raised when an RPCMethod received a pending message.

    The value of this exception is the data returned by
    PTPController._receiveResponse(), a tuple (success, message)
    where success is True if the pending camera message was received
    and False if any other message, or no message at all, was received.
    """


class ShootAction:
    RELEASE_BUTTON = 0
    PRESS_BUTTON = 1
    CLICK_BUTTON = 2


class PTPController:
    """Remote control of a camera with CHDK support.

    A very simple form of RPC is used to control a camera. A Lua
    script is started on the camera that waits for messages from
    the host. When a message is received, some action is performed
    and another message is returned.

    Host-side, RPC methods should be implemented as subclasses of
    RPCMethod. The class' __call__ method should set up required
    parameters, the call cls.invokeRemote(params) and finally call
    _getScriptMessage().

    When a Lua error occurs, the script is started again and an error
    is then raised.

    The Lua script is terminated when the instance of this class are deleted.
    """

    def __init__(self, *args, **kw):
        """Create an instance of PTPController.

        The parameters are directly passed to PTPDevice.__init__().
        """
        self.device = PTPDevice(*args, **kw)
        self.message_pending = False
        self.lua_script = self._buildLuaScript()
        self.script_id = self.device.chdkExecLua(self.lua_script)
        self._buildISOMap()

    def __del__(self):
        # If for example no camera is connected, we get an error
        # before self.device is defined in __init__()
        device = getattr(self, 'device', None)
        if device is None:
            return
        # Stop the camera script.
        if self.device.chdkScriptStatus(self.script_id) & CHDKScriptStatus.RUN:
            self.device.chdkWriteScriptMessage('stop', self.script_id)
        # Try to leave the camera in a clean state: Wait a few seconds
        # until pending messages are consumed and until the
        # "script terminated" message is consumed.

        # XXX 5 seconds might not be long enough for longer running remote
        # calls.
        wait_until = time() + 5
        script_status = self.device.chdkScriptStatus(self.script_id)
        while script_status or wait_until > time():
            if script_status & CHDKScriptStatus.MSG:
                msg = self.device.chdkReadScriptMessage()
                msg_data, msg_type, script_id = msg
                if (msg_type in (CHDKMessageType.RET, CHDKMessageType.ERR) and
                    script_id == self.script_id):
                    # This should be the last message we can expect from the
                    # the camera.
                    if msg_type == CHDKMessageType.ERR:
                        logger.error("Camera error: %r" % (msg, ))
                    break
                else:
                    logger.info("Drained message: %r" % (msg, ))
            else:
                sleep(0.1)
            script_status = self.device.chdkScriptStatus(self.script_id)

    # Trivial message format: Parameters consist of strings separated
    # by spaces. This is obviously very limited but should be sufficient.
    # Each message consistes of a function name, optionally followed
    # by function parameters,
    #
    # The functions themselves are defined in classes derived from
    # RPCMethod, defined below.
    _lua_core = dedent("""
        -- XXX fails sometimes with the error message
        -- "cannot fopen A/CHDK/LUALIB/propcase.LUA"
        -- proptable = require "propcase"
        function parse_msg(msg)
            local result = {}
            local w
            for w in string.gmatch(msg, '[%w_]+') do
                table.insert(result, w)
            end
            return result
        end

        -- status of the shoot button
        -- 0 -> not pressed
        -- 1 -> shoot_half pressed
        -- 2 -> shoot_full pressed
        -- (It seems that the functions is_pressed() or is_key() are
        -- not useful here: it seems that they poll the status of the
        -- physical camera keys, not the fake key presses that are
        -- invoked by the functions press() or click()
        shoot_button_status = 0

        -- it seems that the SX30 must be in alt mode to avoid al least
        -- too frequent crashes in set_zoom().
        -- See also http://chdk.setepontos.com/index.php?topic=9261
        enter_alt()

        while true do
            local msg = read_usb_msg()
            if msg then
                local rpcdat = parse_msg(msg)
                if rpcdat[1] == 'stop' then
                    return 'stopped'
                end
                ftable[rpcdat[1]](rpcdat)
            else
                sleep(50)
            end
        end
    """)

    def _buildLuaScript(self):
        function_definitions = []
        table_entries = []
        for name in self.__class__.__dict__:
            attr = getattr(self, name)
            im_func = getattr(attr, 'im_func', None)
            if not isinstance(im_func, RPCMethod):
                continue
            if callable(attr.lua):
                function_body = attr.lua(self)
            else:
                function_body = attr.lua
            get_params = [
                'local %s = params[%i]' % (attr.params[i], i + 2)
                for i in range(len(attr.params))]
            get_params = '\n'.join(get_params)
            function_definitions.append(
                'function %s(params)\n    %s\n%s\nend' % (
                    attr.lua_name, get_params, dedented_body(function_body)))
            table_entries.append(
                'ftable.%s = %s' % (attr.lua_name, attr.lua_name))
        table_definition = '\n'.join(table_entries)
        function_definitions = '\n'.join(function_definitions)
        return dedent("""\
            %s
            ftable = {}

            %s
            %s
            """) % (function_definitions, table_definition, self._lua_core)

    def luaScriptWithLineNumbers(self):
        script = self.lua_script.split('\n')
        script = ['%4i\t%s' % (index + 1, script[index])
                  for index in xrange(len(script))]
        return '\n'.join(script)

    def _receiveResponse(self):
        """Read a message from the camera.

        Only messages of type CHDKMessageType.USER from the currently
        running script are treated as regular messages. Messages from
        other scripts are simply dropped (but logged); if an error
        message is received, the camera script is started again,
        if necessary.

        return value:

        If a regular user message was received, (True, message_content)
        is returned, else (False, message_content)
        """
        device = self.device
        msg, msg_type, id = device.chdkReadScriptMessage()
        # If no message is available, the script ID seems to be zero.
        if id != self.script_id and msg_type != CHDKMessageType.NONE:
            logger.info(
                'Message dropped. Reason: Message from wrong script. '
                'Content: %s' % ((msg, msg_type, id), ))
        elif msg_type != CHDKMessageType.USER:
            if msg_type == CHDKMessageType.ERR:
                error_message = 'Camera script error:\n%s\n\n%s' % (
                    msg, self.luaScriptWithLineNumbers())
                logger.info(error_message)
                # If we check too quickly if the script is still running,
                # we might not get the right answer...
                sleep(0.1)
                if (device.chdkScriptStatus(self.script_id) &
                    CHDKScriptStatus.RUN == 0):
                    self.script_id = self.device.chdkExecLua(
                        self.lua_script)
                raise LuaError(error_message)
            else:
                logger.info(
                    'Message dropped. Reason: Wrong message type, '
                    'expected type CHDKMessageType.USER, got type %s. '
                    'Content: %s' %
                    (msg_type, (msg, msg_type, id)))
        else:
            self.message_pending = False
            return (True, msg)
        return (False, msg)

    def _getScriptMessage(self, timeout=_DEFAULT_MESSAGE_TIMEOUT):
        """Wait for the first message from the currently running script.

        Messages from older scripts are logged but otherwise ignored.
        When the camera script signals an error, the script is started
        again and a LuaError is raised.
        """
        device = self.device
        wait_until = time() + timeout
        while time() < wait_until:
            if (device.chdkScriptStatus(self.script_id) & CHDKScriptStatus.MSG
                == 0):
                sleep(_MESSAGE_WAIT_DELAY)
                continue
            success, msg = self._receiveResponse()
            if success:
                return msg
        raise PTPControllerError(
            'Timeout waiting for a message from the camera')

    def _buildISOMap(self):
        """Populate self.iso_map for the connected camera."""
        self.iso_map = {0: 'AUTO'}
        iso_mode = 1
        while True:
            try:
                self.setISO(iso_mode)
                self.iso_map[iso_mode] = self.getISO(ISOType.MARKET)
                iso_mode += 1
            except PTPControllerError:
                break

    @classmethod
    def recentImages(cls, start_after, stop_at):
        """An iterator that returns a sequence of image filenames.

        start_after, stop_at: The full path, as used by the camera, of
            image files, e.g., A/DCIM/114___12/IMG_0022.JPG

        It returns a sequence of file paths as can be expected to be
        created by the camera, beginning with the first name coming
        after start_after, the last one is identical to stop_at.

        The template of the "non-sequence" part of the path names
        ('A/DCIM/%03d___12/IMG_%04i.JPG' in the exampe name above)
         is taken from the parameter stop_at.

        Note that this method is _not_ able to deal with the situation
        that start_after is None, as returned by lastImageName() for
        an empty SD card.
        """
        if start_after is None or stop_at is None:
            raise PTPControllerError('Real file paths required')
        img_path_re = re.compile(r'^A/DCIM/(\d\d\d)(.{10})(\d\d\d\d)(.{4})$')
        parts = img_path_re.search(stop_at)
        if parts is None:
            raise PTPControllerError('Invalid file path: %s' % stop_at)
        dir_stop, part1, file_stop, part2 = parts.groups()
        template = 'A/DCIM/%%03i%s%%04i%s' % (part1, part2)
        dir_stop = int(dir_stop)
        file_stop = int(file_stop)

        parts = img_path_re.search(start_after)
        if parts is None:
            raise PTPControllerError('Invalid file path: %s' % start_after)
        dir_current, ignore, file_current, ignore = parts.groups()
        dir_current = int(dir_current)
        file_current = int(file_current) + 1
        if file_current > 9999:
            file_current = 1
            dir_current += 1

        while (dir_current, file_current) <= (dir_stop, file_stop):
            yield template % (dir_current, file_current)
            file_current += 1
            if file_current > 9999:
                file_current = 1
                dir_current += 1

    # The default timeout of 5 seconds is too short for the A810, at least
    # for shoot(CLICK_BUTTON)
    def shoot(self, mode=ShootAction.CLICK_BUTTON, click_time=0.1,
              keep_half_shoot=False, timeout=10):
        """Make a photo.

        parameter mode: A value defined in class ShootAction
        parameter click_time: The time in sec during which the shoot button
            is pressed. Only used for mode CLICK_BUTTON
        parameter keep_half_shoot: In modes CLICK_BUTTON, RELEASE_BUTTON,
            the shoot button is kept in status "half pressed" when the
            method finishes. Otherwise, "shoot_half" is released too.
            The parameter is ignored for PRESS_BUTTON.
        """
        # it seems that the camera can become really confused if the shoot
        # button is pressed in playback mode.
        if not self.getMode()[0]:
            raise PTPControllerError('not in recording mode')
        wait_until = time() + timeout
        if mode == ShootAction.CLICK_BUTTON:
            self.shoot(ShootAction.PRESS_BUTTON, click_time, keep_half_shoot,
                       timeout)
            sleep(click_time)
            self.shoot(ShootAction.RELEASE_BUTTON, click_time, keep_half_shoot,
                       timeout)
        elif mode == ShootAction.PRESS_BUTTON:
            self.pressButton("shoot_half")
            is_shooting = self.getShooting()
            while not is_shooting and time() < wait_until:
                sleep(0.05)
                is_shooting = self.getShooting()
            if not is_shooting:
                raise PTPControllerError('Timeout pressing shoot_half')
            self.pressButton('shoot_full')
        else:
            if keep_half_shoot:
                self.releaseButton('shoot_full_only')
            else:
                self.releaseButton('shoot_full')
                is_shooting = self.getShooting()
                while is_shooting and time() < wait_until:
                    sleep(0.05)
                    is_shooting = self.getShooting()
                # XXX do we really need a timeout here?
                if is_shooting:
                    raise PTPControllerError('Timeout releasing shoot_full')

    def shootHalf(self, enable, wait_until_ready=False,
                  timeout=_DEFAULT_MESSAGE_TIMEOUT):
        """Press or release the "shoot_half" button.

        parameter enable: When True, the shoot_half button is pressed,
            else it is released.
        parameter wait_until_ready: Wait until get_shooting() == value
            before returning.
        """
        # it seems that the camera can become really confused if the shoot
        # button is pressed in playback mode.
        if not self.getMode()[0]:
            raise PTPControllerError('not in recording mode')
        wait_until = time() + timeout
        if enable:
            self.pressButton('shoot_half')
            final_status = True
        else:
            self.releaseButton('shoot_half')
            final_status = False
        if wait_until_ready:
            while time() < wait_until and final_status != self.getShooting():
                sleep(0.05)
            if self.getShooting() != final_status:
                raise PTPCOntrollerError(
                    'Timeout pressing/releasing shoot_half')


class RPCMethod:
    """Instances of classes derived from this class will be added
    as methods to class PTPController.

    This allowed the definition of Lua functions executed on the camera
    in "direct neighbourhood" of the corresponding Python code that
    starts the execution of the Lua function.

    Derived classes must define these class attributes:

        name: used as the name of the method of PTPController.
        lua: a string containing the body of a Lua function.
        lua_name (optional): the name of the Lua function. If not defined,
            the the attribute 'name' is used.
    """
    @classmethod
    def invokeRemote(cls, self, *params, **kw):
        # check if the camera should still send any message.
        if self.message_pending:
            raise StuckMessage(self._receiveResponse())
        # xxx str(p) is quite naive.
        params = ' '.join(str(p) for p in params)
        self.device.chdkWriteScriptMessage(
            '%s %s' % (cls.lua_name, params), self.script_id)
        if not kw.get('no_response', False):
            self.message_pending = True

    @classmethod
    def  __call__(cls, self, *args, **kw):
        """cls allows access to class attributes; self allows access
        to properties of the PTPController instance.
        """
        raise NotImplemented


class Test(RPCMethod):
    """Various test functions.

    parameters: action, value

    action == 'send_message':
        the text from value is sent back to the host, but this method
        does not consume the message. Note that this deliberately
        screws up the request/response concept of the host <-> camera
        communication. Do not use this in any real application.
    action == 'echo':
        the text from value is sent back to the host; this method
        consumes the message and returns it.
    action == 'runtime_error':
        a runtime error occurs; this method waits for the
        corresponding message from the camera; when the message
        is received, a LuaError is raised (in _getScriptMessage).
    action == 'timeout':
        The Lua script waits for value * 2 seconds before it sends
        a response, while this method waits only value seconds for
        the response. In other words, a timeout exception will be raised
        and a message is stuck.
    """
    name = 'rpcTest'
    params = ('action', 'value')
    lua = """\
    if action == 'send_message' or action == 'echo' then
        write_usb_msg(value)
    elseif action == 'runtime_error' then
        error(value)
    else
        value = 0 + value
        sleep(value)
        write_usb_msg('ready')
    end -- silently ignore any invalid actions
    """

    @classmethod
    def __call__(cls, self, action, value):
        if action not in ('send_message', 'echo', 'runtime_error', 'timeout'):
            raise PTPControllerError('Invalid action value: %r' % action)
        if action == 'timeout':
            host_timeout = value
            value = 2000 * value
        else:
            host_timeout = _DEFAULT_MESSAGE_TIMEOUT
        cls.invokeRemote(self, action, value)
        if action == 'send_message':
            return
        return self._getScriptMessage(timeout=host_timeout)


def split_lua_table_string(s):
    """Split a string with Lua table representation into
    [(k1, v1), (k2, v2)...]
    """
    # the last character should always be a '\n'
    return [e.split('\t', 1) for e in s[:-1].split('\n')]

to_bool = {
    'false': False,
    'true': True,
    }

def parse_mode_string(s):
    """Parse the string represneting the Lua table returned by CHDK's
    get_mode() function. This is supposed to be a table like
    '1\tfalse\n2\tfalse\n3\t2562\n'

    see http://chdk.wikia.com/wiki/Lua/Lua_Reference#get_mode :
    return data is (bool is_record, bool is_video, number mode)
    """
    # we don't need the keys
    data = [d[1] for d in split_lua_table_string(s)]
    return to_bool[data[0]], to_bool[data[1]], int(data[2])


class SetMode(RPCMethod):
    """Set the camera into the given mode.

    mode == 1 -> record
    mode == 0 -> playback

    return: current mode (bool is_record, bool is_video, number mode)
    """
    name = 'setMode'
    params = ('mode', )
    # Polling the status too often can confuse the camera.
    # Doing it twice per second seems fine.
    # And don't call set_mode() for the current state. Confuses
    # the camera too.
    # Note that the wiki page chdk/doc/Script_commands.htm says
    # that get_mode() returns a table with three elements. But if
    # used like write_usb_msg(get_mode()), we just get a bool back.
    # The variant below works fine though...
    lua = """\
        mode = 0 + mode
        local bool_mode = mode ~= 0
        local count
        if get_mode() ~= bool_mode then
            if mode == 0 then
                -- If the camera is currently shooting, we must first
                -- release the shoot button and wait until shooting is
                -- done, otherwise the camera may crash.
                if shoot_button_status ~= 0 then
                    release('shoot_full')
                    shoot_button_status = 0
                end
                -- no timeout here: A Python timeout error is preferable to
                -- confused camera.
                while get_shooting() == true do
                    sleep(100)
                end
            end
            count = 0
            switch_mode_usb(mode)
            -- sleep(100) confuses the SX100.
            sleep(500)
            while get_mode() ~= bool_mode and count < 10 do
                sleep(500)
                count = count + 1
            end
        end
        write_usb_msg({get_mode()})
        """

    @classmethod
    def __call__(cls, self, mode):
        cls.invokeRemote(self, int(mode))
        return parse_mode_string(self._getScriptMessage(timeout=30))


class GetMode(RPCMethod):
    """Get the current camera mode.

    return: current mode (bool is_record, bool is_video, number_of_mode)
    The lower 8 bit of number_of_mode represnt the mode number as used
    in the dictionary returned by supportedCaptureModes().
    """
    name = 'getMode'
    params = ()
    lua = """\
        write_usb_msg({get_mode()})
        """

    @classmethod
    def __call__(cls, self):
        cls.invokeRemote(self)
        return parse_mode_string(self._getScriptMessage())


class GetShooting(RPCMethod):
    """Call the Lua function get_shooting() and return its result.
    """
    name = 'getShooting'
    params = ()
    # A modified copy of the CHDK file CHDK/SCRIPTS/shoot.lua.
    lua = """\
        write_usb_msg(get_shooting())
    """

    @classmethod
    def __call__(cls, self):
        cls.invokeRemote(self)
        # XXX The SX30 sometimes returns a Lua error. No line number or
        # other details specified...
        return self._getScriptMessage()


class ExposureCount(RPCMethod):
    """Return the current exposure count.

    Calls the Lua function get_exp_count().

    According to an example in http://chdk.wikia.com/wiki/Lua the
    returned value should be an integer in the range 1..9999
    """
    name = 'exposureCount'
    params = ()
    lua = """\
        write_usb_msg(get_exp_count())
    """

    @classmethod
    def __call__(cls, self):
        cls.invokeRemote(self)
        return int(self._getScriptMessage())


class LastImageName(RPCMethod):
    """Return the "highest numbered" image file.

    According to http://www.exif.org/dcf.PDF , the images are stored
    in path names like 'DCIM/\d{3}\w{5}/\w{4}\d{4}\....', expressed
    as a Python regex. (The exact definition is a bit stricter...)

    The digits of the directory name are numbers between 100 and 999;
    the digits of the file name are numbers between 1 and 9999.

    Assuming that a camera will always increase but never decrease
    these numbers, we can figure out which is the most recently
    recorded picture or video.

    XXX The current implementation does not deal properly with the
    case that there is nore than one file with the same number in
    one directory, as described in section 3.2.1 of the specification
    mentioned above.

    Corner cases are not treated properly. Most importantly, if
    the DCIM directory was popluated on camera A and is then used
    in camera B, and if the directory/file counters of camera A are
    higher than those of camera B, lastImageName() will return
    a useless result on camera B.
    """
    name = 'lastImageName'
    params = ()
    lua = """\
        function dircomp(d1, d2)
            -- compare the digits of a DCIM subdirectory.
            return string.sub(d1, 1, 3) < string.sub(d2, 1, 3)
        end

        function file_comp(f1, f2)
            -- compare the digits of an image/video file in a DCIM subdirectory.
            return string.sub(f1, 5, 8) < string.sub(f2, 5, 9)
        end

        local entries = os.listdir("A/DCIM")
        local max_dir = nil
        local max_file = nil
        local i
        if #entries == 0 then
            write_usb_msg(nil)
            return
        end
        table.sort(entries, dircomp)
        for i = table.getn(entries), 1, -1 do
            local dir_name = entries[i]
            if string.find(dir_name, '^%d%d%d') then
                dir_name = "A/DCIM/" .. dir_name
                if os.stat(dir_name)['is_dir'] then
                    max_dir = dir_name
                    break
                end
            end
        end
        if max_dir == nil then
            write_usb_msg(nil)
            return
        end
        -- Without the sleep(1), the SX30 powers off quite reliably...
        sleep(1)
        entries = os.listdir(max_dir)
        table.sort(entries, file_comp)
        for i = table.getn(entries), 1, -1 do
            local filename = entries[i]
            if string.find(filename, '^....%d%d%d%d') then
                -- XXX would it make sense to also check if we have a
                -- real file, not a directory? Or the name's suffix?
                write_usb_msg(max_dir .. '/' .. filename)
                return
            end
        end
        -- this happens if we have an empty directory.
        write_usb_msg(max_dir)
        """

    @classmethod
    def __call__(cls, self):
        cls.invokeRemote(self)
        return self._getScriptMessage()


class ClickButton(RPCMethod):
    name = 'clickButton'
    params = ('button_name', )
    lua = """\
        click(button_name)
    """

    @classmethod
    def __call__(cls, self, button_name):
        # these button should be cotrolled via shoot(), shootHalf()
        assert button_name not in ('shoot_full', 'shoot_full_only',
                                   'shoot_half')
        cls.invokeRemote(self, button_name, no_response=True)


class PressButton(RPCMethod):
    name = 'pressButton'
    params = ('button_name', )
    lua = """\
        press(button_name)
        if button_name == 'shoot_half' then
            shoot_button_status = 1
        elseif button_name == 'shoot_full' or button_name == 'shoot_full_only'
          then
            shoot_button_status = 2
        end
    """

    @classmethod
    def __call__(cls, self, button_name):
        cls.invokeRemote(self, button_name, no_response=True)


class ReleaseButton(RPCMethod):
    name = 'releaseButton'
    params = ('button_name', )
    lua = """\
        release(button_name)
        if button_name == 'shoot_full_only' then
            shoot_button_status = 1
        elseif button_name == 'shoot_full' or button_name == 'shoot_half' then
            shoot_button_status = 0
        end
    """

    @classmethod
    def __call__(cls, self, button_name):
        cls.invokeRemote(self, button_name, no_response=True)


class ZoomSteps(RPCMethod):
    """Return the number of possible zoom steps."""
    name = 'zoomSteps'
    params = ()
    lua = """\
        write_usb_msg(get_zoom_steps())
    """

    @classmethod
    def __call__(cls, self):
        cls.invokeRemote(self)
        return self._getScriptMessage()


class ZoomSpeed(RPCMethod):
    """Set the zoom speed.

    The speed value passed to this method must be an integer greater or
    equal to 5 and less or equal to 100.
    """
    name = 'zoomSpeed'
    params = ('speed', )
    lua = """\
        set_zoom_speed(speed)
        write_usb_msg('ok')
    """

    @classmethod
    def __call__(cls, self, speed):
        speed = int(speed)
        if not 5 <= speed <= 100:
            raise PTPControllerError('Invalid zoom speed value: %i' % speed)
        cls.invokeRemote(self, speed)
        self._getScriptMessage()

class SetZoom(RPCMethod):
    """Set the zoom value.

    The value passed to this method should be greater than or equal to 0 and
    less than zoomSteps().

    Note that this method may be unreliable on some cameras. The SX30
    is known to crash occasionally; the SX100 crashes reliably when
    the Lua function set_zoom() is called.
    """
    name = 'setZoom'
    params = ('zoom', )
    # XXX check that shoot/shoot_half is not pressed!
    _lua_default = """\
        zoom = 0 + zoom
        set_zoom(zoom)
        write_usb_msg('ok')
    """

    # When continuous AF is enabled, the SX40 shuts off a few seconds
    # after the set_zoom() call. This can be avoided by a short
    # shoot_half click.
    _lua_SX40 = """\
        zoom = 0 + zoom
        set_zoom(zoom)
        write_usb_msg('ok')
        if shoot_button_status == 0 then
            press('shoot_half')
            sleep(50)
            release('shoot_half')
        end
    """

    def lua(self, controller):
        if controller.device.model == 'Canon PowerShot SX40 HS':
            return self._lua_SX40
        return self._lua_default

    @classmethod
    def __call__(cls, self, zoom):
        zoom = int(zoom)
        cls.invokeRemote(self, zoom)
        self._getScriptMessage()

class GetZoom(RPCMethod):
    """Get the current zoom value."""
    name = 'getZoom'
    params = ()
    lua = """\
        write_usb_msg(get_zoom())
    """

    @classmethod
    def __call__(cls, self):
        cls.invokeRemote(self)
        return self._getScriptMessage()


class SupportedCaptureModes(RPCMethod):
    """Return the capture modes supported by the camera.

    The result is a dictionary mapping mode names to integers.

    See also getMode() and setCaptureMode().
    """
    name = 'supportedCaptureModes'
    params = ()
    lua = """\
        local capture_modes = require('GEN/modelist')
        local valid_modes = {}
        local set_item = function(v, k)
            if is_capture_mode_valid(v) then
                valid_modes[k] = v
            end
        end
        table.foreach(capture_modes, set_item)
        write_usb_msg(valid_modes)
    """
    _cached_modes = None

    def __call__(cls, self):
        modes = getattr(self, '_cached_capture_modes', None)
        if modes is None:
            cls.invokeRemote(self)
            modes = {}
            for k, v in split_lua_table_string(self._getScriptMessage()):
                modes[k] = int(v)
            self._cached_capture_modes = modes
        return modes


class SetCaptureMode(RPCMethod):
    """Set the capture mode. The parameter mode must appear in the
    keys or the values returned by supportedCaptureModes().

    Return: True if the mode could be set else False.
    """
    name = 'setCaptureMode'
    params = ('mode', )
    lua = """\
        mode = 0 + mode
        write_usb_msg(set_capture_mode(mode))
    """

    @classmethod
    def __call__(cls, self, mode):
        if mode not in self.supportedCaptureModes().values():
            try:
                mode = self.supportedCaptureModes()[mode]
            except KeyError:
                raise PTPControllerError('Invalid capture mode: %r' % mode)
            cls.invokeRemote(self, mode)
            return self._getScriptMessage()

class ISOType:
    """Parameter values that can be passed to PTPController.getMode().
    """
    @property
    def INDEX(self):
        """PTPController.getMode() returns the current mode's index."""
        return 0

    @property
    def REAL(self):
        """PTPController.getMode() returns the real ISO value."""
        return 1

    @property
    def MARKET(self):
        """PTPController.getMode() returns the real ISO value."""
        return 2


class GetISO(RPCMethod):
    """Return the current ISO setting.

    What data is returned, depends on the value of the parameter iso_type.

    If iso_type == ISOType.INDEX, the number od currently active ISO
    setting is returned:

        0 -> automatic mode
        1 -> lowest ISO setting (ISO 80 on most cameras)
        ...
        N -> highest ISO setting (ISO 800 or 1600 on most cameras)

    If iso_type == ISOType.REAL, the "real" setting used by the camera
    is returned.

    If iso_type == ISOType.MARKET, the ISO value as displayed by the
    camera is returned.

    Note that the values returned for ISOType.MARKET and ISOType.REAL
    require a "shoot_half" press in order to return a useful value in
    auto ISO mode.

    See
    http://chdk.wikia.com/wiki/CHDK_firmware_usage/AllBest#Show_.27Real.27_ISO
    for an explanation of the difference between "real" and "market" ISO
    values.
    """
    name = 'getISO'
    params = ('iso_type', )
    lua = """\
        if iso_type == 0 then
            write_usb_msg(get_iso_mode())
        elseif iso_type == 1 then
            write_usb_msg(get_iso_real())
        else
            write_usb_msg(get_iso_market())
        end
    """

    @classmethod
    def __call__(cls, self, iso_type):
        cls.invokeRemote(self, iso_type)
        return self._getScriptMessage()


class SetISO(RPCMethod):
    """Set the ISO mode.

    The parameter 'iso' must be a valid number of an ISO mode, i.e.,
    it must appear as a key of the dictionary iso_map of a PTPcontroller.
    """
    name = 'setISO'
    params = ('iso', )
    lua = """\
        iso = 0 + iso
        set_iso_mode(iso)
        write_usb_msg(get_iso_mode())
    """

    @classmethod
    def __call__(cls, self, iso):
        cls.invokeRemote(self, iso)
        result = self._getScriptMessage()
        if result != iso:
            raise PTPControllerError('Canont set ISO value %r' % iso)
        return result


class GetFocus(RPCMethod):
    """Retrieve focus related data.

    Return a tuple with focus related information.

    The tuple contains the results of these CHDK function calls:
    (get_focus_state(). get_focus(), get_focus_mode(), get_shooting())

    Quoting http://chdk.wikia.com/wiki/CHDK_Scripting_Cross_Reference_Page:

    get_focus_state() returns focus status, > 0 focus successful,
    =0 not successful, < 0 MF.

    get_focus() gets current focus distance in mm.

    get_shooting() return boolean true if half_press active and
    focus+exposure is set , false otherwise.
    """
    name = 'getFocus'
    params = ()
    # get_shooting() disabled: still crashing
    lua = """\
        result = {
            get_focus_state(),
            get_focus(),
            get_shooting(),
            }
        write_usb_msg(result)
    """

    @classmethod
    def __call__(cls, self):
        cls.invokeRemote(self)
        result = split_lua_table_string(self._getScriptMessage())
        result = dict(result)
        return (int(result['1']),
                int(result['2']),
                True if result['3'] == 'true' else False,
            )


def dedented_body(body):
    body = dedent(body).split('\n')
    body = ['    %s' % line if line else '' for line in body]
    return '\n'.join(body)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
logger.addHandler(log_handler)

module = sys.modules[__name__]
rpc_methods = [obj for obj in module.__dict__.values()
               if type(obj) == type and issubclass(obj, RPCMethod)
                  and obj is not RPCMethod]
existing_attributes = set(PTPController.__dict__.keys())
new_attributes = set()
for cls in rpc_methods:
    if cls.name in new_attributes:
        raise ValueError('RPC method %s already defined' % cls.name)
    if cls.name in existing_attributes:
        raise ValueError(
            'RPC method %s overrides base class attribute' % cls.name)
    if getattr(cls, 'lua_name', None) is None:
        cls.lua_name = cls.name
    inst = cls()
    inst.__name__ = cls.name
    new_attributes.add(cls.name)
    setattr(PTPController, cls.name, MethodType(inst, None, PTPController))
    # keep the module's dict clean: We don't need all the RPCMethod classes
    # there any more, they just clutter the output of "help(devicecontroller)"
    del module.__dict__[cls.__name__]
