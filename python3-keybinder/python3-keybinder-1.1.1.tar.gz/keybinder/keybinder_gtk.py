#!/usr/bin/env python3

# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import Gdk
from gi.repository import Gtk
import threading
from Xlib import X
from Xlib import XK
from Xlib.ext import record
from Xlib.protocol import rq

from keybinder import keybinder

gdk_modifiers = (
        Gdk.ModifierType.CONTROL_MASK,
        Gdk.ModifierType.SHIFT_MASK,
        Gdk.ModifierType.SUPER_MASK,
        Gdk.ModifierType.HYPER_MASK,
        Gdk.ModifierType.META_MASK,
        )

known_modifiers_mask = 0
for modifier in gdk_modifiers:
    if "Mod" not in Gtk.accelerator_name (0, modifier):
        known_modifiers_mask |= modifier

class KeybinderGtk(threading.Thread):
    _keys = {
            'callback': [],
            'code': [],
            'str': [],
            'mod': [],
            }
    def __init__(self):
        super().__init__()
        self.setDaemon(True)
        self.binded = False

    def record_callback(self, reply):
        '''convert X keycode to GDK keycode, and compare with _keys

        reply is a tuple containing X data
        '''
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            #print('* received swapped protocol data, cowardly ignored')
            return
        if len(reply.data) == 0 or reply.data[0] < 2:
            # not an event
            return

        data = reply.data
        while len(data) > 0:
            event, data = rq.EventField(None).parse_binary_value(data,
                    keybinder.record_dpy.display, None, None)

            #keysym = keybinder.local_dpy.keycode_to_keysym(event.detail, 0)
            #print(keysym)
            if event.type == X.KeyRelease and  event.detail in self._keys['code']:
                modifiers = event.state & known_modifiers_mask
                for i in range(len(self._keys['code'])):
                    if modifiers == self._keys['mod'][i] and \
                            event.detail == self._keys['code'][i]:
                        # TODO: using GLib.idle_add()
                        self._keys['callback'][i]()
                        break

    def register(self, key, callback):
        if key in self._keys['str']:
            index = self._keys['str'].index(key)
            self._keys['callback'].remove(self._keys['callback'][index])
            self._keys['mod'].remove(self._keys['mod'][index])
            self._keys['code'].remove(self._keys['code'][index])
            self._keys['str'].remove(key)

        self._keys['str'].append(key)
        self._keys['callback'].append(callback)
        k, mod = Gtk.accelerator_parse(key)
        mod = int(mod)
        self._keys['mod'].append(mod)

        keycode = keybinder.local_dpy.keysym_to_keycode(k)
        self._keys['code'].append(keycode)

    def unregister(self, key):
        if key not in self._keys['str']:
            return False
        index = self._keys['str'].index(key)
        self._keys['str'].remove(key)

    def run(self):
        self.binded = True
        keybinder.bind(self.record_callback)

    def stop(self):
        keybinder.unbind()
