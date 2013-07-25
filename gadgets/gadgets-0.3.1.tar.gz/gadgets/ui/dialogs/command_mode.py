import curses, time
from gadgets.ui.window import Window
from gadgets.ui.dialogs.prompt import Prompt
from gadgets.ui.dialogs.alert import Alert

KEYCODE_ENTER = 10
KEYCODE_ESC = 27

class CommandMode(Window):
    """
    
    """

    def __init__(self, parent):
        self._parent = parent
        self._lock = parent._lock
        self._command_mode = self._get_command_mode()
        self.is_active = False

    def _get_command_mode(self):
        return {
            'keys': [],
            'i': -1
        }

    @property
    def keys(self):
        return self._command_mode['keys']

    def __call__(self, x):
        if x == KEYCODE_ESC:
            self._command_mode = self._get_command_mode()
            self.is_active = False
        elif len(self._command_mode['keys']) == 2 and x == KEYCODE_ENTER:
            self._do_command()
        elif len(self._command_mode['keys']) == 2 and x == ord('a'):
            argument = self._get_argument()
            if argument:
                self._do_command(argument)
        else:
            self._update_command_mode(x)
        
    def _get_argument(self):
        self._lock.acquire()
        p = Prompt('value', str)
        argument = p(self._parent._screen)
        try:
            val, units = argument.split(' ')
        except ValueError:
            a = Alert('Error', 'enter a value and its units')
            a(self._parent._screen)
            return_value = None
        else:
            return_value = {'value': float(val), 'units': units}
        self._lock.release()
        return return_value

    def _do_command(self, argument={}):
        keys = self._command_mode['keys']
        d = self._parent._data['locations']
        for i, name in enumerate(self._command_mode['keys']):
            if i == 0:
                d = d[name]['output']
            else:
                d = d[name]
        status = 'off' if d['value'] else 'on'
        command = self._parent._getter.commands[keys[0]][keys[1]][status]
        self._parent.sockets.send(str(command), argument)

    def _get_devices(self, data):
        devices = []
        for location, val in data.iteritems():
            for dev in val.get('output', {}).keys():
                devices.append((location, dev))
        return devices

    def _update_command_mode(self, x):
        """
        down arrow = 258
        up arrow =   259
        C-p      =   16
        p        =   112
        C-n      =   14
        n        =   110
        """
        direction = None
        i = self._command_mode['i']
        if x == 258 or x == 14 or x == 110:
            i += 1
        elif x == 259 or x == 16 or x == 112:
            i -= 1
        else:
            return
        d = self._parent._data.get('locations', {})
        devices = self._get_devices(d)
        if i >= len(devices):
            i = 0
        elif i < 0:
            i = len(devices) - 1
        self._command_mode['keys'] = devices[i]
        self._command_mode['i'] = i
        
