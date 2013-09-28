#
# UIMap.py -- User Interface Mapper plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from ginga.qtw.QtHelp import QtGui, QtCore
from ginga.qtw import QtHelp

from ginga import GingaPlugin
from ginga.misc import Bunch


class UIMap(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(UIMap, self).__init__(fv, fitsimage)

        self.layertag = 'uimap'

        self.dc = self.fv.getDrawClasses()

        canvas = self.dc.DrawingCanvas()
        canvas.enable_draw(False)

        ## for name in ('cursor', 'wheel', 'draw'):
        ##     for action in ('down', 'move', 'up'):
        ##         canvas.set_callback('%s-%s' % (name, action),
        ##                             self.btn_action, name)

        ## canvas.set_drawtype('rectangle', color='cyan', linestyle='dash',
        ##                     drawdims=True)
        ## canvas.set_callback('draw-event', self.setpickregion)
        canvas.setSurface(self.fitsimage)
        self.canvas = canvas

        self.t_ = self.fitsimage.get_settings()
        ## for name in ('autocut_method', 'autocut_params'):
        ##     self.t_.getSetting(name).add_callback('set', self.set_autocuts_ext_cb)

        ## self.t_.setdefault('wcs_coords', 'icrs')
        ## self.t_.setdefault('wcs_display', 'sexagesimal')

        # Get list of mouse possibilities
        bindings = self.fitsimage.get_bindings()

        self.button_actions = []
        for attrname in dir(bindings):
            if attrname.startswith('ms_'):
                self.button_actions.append(attrname[3:])
                
        self.scroll_actions = []
        for attrname in dir(bindings):
            if attrname.startswith('sc_'):
                self.scroll_actions.append(attrname[3:])
                
        self.key_actions = list(bindings.get_key_features())
        self.key_actions.sort()
                
        bindmap = self.fitsimage.get_bindmap()

        self.button_options = list(bindmap.get_buttons())
        self.button_options.sort()

        options = set(bindmap.get_modifiers())
        options = list(options)
        options.sort()
        self.modifier_options = ['none'] + options

        self.btnmap = {
            'cursor': 'pan',
            'draw': 'cmapwarp',
            }
        

    def build_gui(self, container):
        sw = QtGui.QScrollArea()

        twidget = QtHelp.VBox()
        sp = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                               QtGui.QSizePolicy.Fixed)
        twidget.setSizePolicy(sp)
        vbox = twidget.layout()
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(2)
        sw.setWidgetResizable(True)
        sw.setWidget(twidget)

        # MOUSE MAPPING OPTIONS
        fr = QtHelp.Frame("Buttons")

        captions = (('Modifier', 'combobox'),
                    ('Button', 'combobox'),
                    ('Action', 'combobox'),
                    ('Set', 'button'),
                    )
        w, b = QtHelp.build_info(captions)
        self.w.b_modifier = b.modifier
        self.w.b_button = b.button
        self.w.b_action = b.action
        b.modifier.setToolTip("Choose modifier")
        b.button.setToolTip("Choose button")
        b.action.setToolTip("Choose action")
        b.set.setToolTip("Set the mapping")
        b.set.clicked.connect(self.set_button_cb)
        fr.layout().addWidget(w, stretch=1, alignment=QtCore.Qt.AlignLeft)
        vbox.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)

        combobox = b.modifier
        options = []
        index = 0
        for name in self.modifier_options:
            options.append(name)
            combobox.addItem(name)
            index += 1

        combobox = b.button
        options = []
        index = 0
        for name in self.button_options:
            options.append(name)
            combobox.addItem(name)
            index += 1

        combobox = b.action
        options = []
        index = 0
        for name in self.button_actions:
            options.append(name)
            combobox.addItem(name)
            index += 1
        # cmap_name = self.t_.get('color_map', "ramp")
        # try:
        #     index = self.cmap_names.index(cmap_name)
        # except Exception:
        #     index = self.cmap_names.index('ramp')
        index = 0
        combobox.setCurrentIndex(index)

        # SCROLL MAPPING OPTIONS
        fr = QtHelp.Frame("Scrolling")

        captions = (('Modifier', 'combobox'),
                    ('Action', 'combobox'),
                    )
        w, b = QtHelp.build_info(captions)
        self.w.s_modifier = b.modifier
        self.w.s_action = b.action
        b.modifier.setToolTip("Choose modifier")
        b.action.setToolTip("Choose action")
        fr.layout().addWidget(w, stretch=1, alignment=QtCore.Qt.AlignLeft)
        vbox.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)

        combobox = b.modifier
        options = []
        index = 0
        for name in self.modifier_options:
            options.append(name)
            combobox.addItem(name)
            index += 1

        combobox = b.action
        options = []
        index = 0
        for name in self.scroll_actions:
            options.append(name)
            combobox.addItem(name)
            index += 1
            
        # KEY MAPPING OPTIONS
        fr = QtHelp.Frame("Keystrokes")

        captions = (('Action', 'combobox'),
                    ('Keys', 'label'),
                    ('Capture', 'label'),
                    ('Clear', 'button'),
                    )
        w, b = QtHelp.build_info(captions)
        self.w.k_action = b.action
        self.w.k_keys = b['keys']
        b.action.setToolTip("Choose action")
        self.w.k_keys.setToolTip("Keys that invoke it")
        fr.layout().addWidget(w, stretch=1, alignment=QtCore.Qt.AlignLeft)
        vbox.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)

        combobox = b.action
        options = []
        index = 0
        for name in self.key_actions:
            options.append(name)
            combobox.addItem(name)
            index += 1
        combobox.activated.connect(self.set_keyfeat_cb)

        btns = QtHelp.HBox()
        layout = btns.layout()
        layout.setSpacing(3)

        btn = QtGui.QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)
        vbox.addWidget(btns, stretch=0, alignment=QtCore.Qt.AlignLeft)

        #container.addWidget(sw, stretch=1, alignment=QtCore.Qt.AlignTop)
        container.addWidget(sw, stretch=1)
        
        self.gui_up = True
        
    def set_button_cb(self):
        # get button alias
        idx = self.w.b_button.currentIndex()
        alias = self.button_options[idx]

        # get modifier
        idx = self.w.b_modifier.currentIndex()
        modifier = self.modifier_options[idx]
        if modifier == 'none':
            modifier = None

        # get action
        idx = self.w.b_action.currentIndex()
        event = self.button_actions[idx]

        bindmap = self.fitsimage.get_bindmap()
        bindmap.map_event(modifier, alias, event)

    def set_keyfeat_cb(self, index):
        # get key feature
        keyfeat = self.key_actions[index]
        bindings = self.fitsimage.get_bindings()
        print "getting keys"
        keys = bindings.get_key_bindings(keyfeat)
        print "keys are", keys

        self.w.k_keys.setText(', '.join(keys))

    def btn_action(self, canvas, action, data_x, data_y, button):
        print "1"
        bindings = self.fitsimage.get_bindings()
        print "2"
        method = getattr(bindings, "ms_%s" % (self.btnmap[button]))
        print "calling ", method
        return method(self.fitsimage, action, data_x, data_y)

    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_operation_channel(chname, str(self))
        return True
        
    def start(self):
        # insert layer if it is not already
        try:
            obj = self.fitsimage.getObjectByTag(self.layertag)

        except KeyError:
            # Add canvas layer
            self.fitsimage.add(self.canvas, tag=self.layertag)
            
        self.resume()

    def pause(self):
        self.canvas.ui_setActive(False)
        
    def resume(self):
        self.canvas.ui_setActive(True)
        
    def stop(self):
        # deactivate the canvas 
        self.canvas.ui_setActive(False)
        try:
            self.fitsimage.deleteObjectByTag(self.layertag)
        except:
            pass
        self.gui_up = False
        
    def redo(self):
        pass

    def __str__(self):
        return 'uimap'
    
#END
