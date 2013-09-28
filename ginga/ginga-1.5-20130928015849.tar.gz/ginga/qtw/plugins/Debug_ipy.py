#
# Debug.py -- Debugging plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import atexit

from ginga import GingaPlugin

from ginga.qtw.QtHelp import QtGui, QtCore

from code import InteractiveConsole

have_ipython = False
try:
    from IPython.zmq.ipkernel import IPKernelApp
    from IPython.lib.kernel import find_connection_file
    from IPython.frontend.qt.kernelmanager import QtKernelManager
    from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
    from IPython.utils.traitlets import TraitError
    have_ipython = True
except Exception, e:
    # TODO: signal this to the user
    pass

class Shell(InteractiveConsole):
    def __init__(self, *args, **kwdargs):
        InteractiveConsole.__init__(self, *args, **kwdargs)

        self.debugObj = None

    def push(self, data):
        self.write('>>> ' + data + '\n')
        InteractiveConsole.push(self, data)

    def write(self, data):
        if self.debugObj != None:
            self.debugObj.write(data)

        
class Debug(GingaPlugin.GlobalPlugin):

    def __init__(self, fv):
        # superclass defines some variables for us, like logger
        super(Debug, self).__init__(fv)

        self.namespace = dict(fv=self.fv,
                              reloadLocalPlugin=self.reloadLocalPlugin,
                              reloadGlobalPlugin=self.reloadGlobalPlugin)

    def build_gui(self, container):
        rvbox = container

        if have_ipython:
            widget = self.terminal_widget()
            rvbox.addWidget(widget, stretch=1)

        else:
            self.msgFont = self.fv.getFont("fixedFont", 14)
            tw = QtGui.QTextEdit()
            #tw.setLineWrapMode(??)
            ## tw.set_left_margin(4)
            ## tw.set_right_margin(4)
            tw.setReadOnly(True)
            ## tw.set_left_margin(4)
            ## tw.set_right_margin(4)
            tw.setCurrentFont(self.msgFont)
            self.tw = tw
            self.history = []
            self.histmax = 10

            sw = QtGui.QScrollArea()
            sw.setWidgetResizable(True)
            #sw.set_border_width(2)
            sw.setWidget(self.tw)

            rvbox.addWidget(sw, stretch=1)
            sw.show()

            self.entry = QtGui.QLineEdit()
            rvbox.addWidget(self.entry, stretch=0)
            self.entry.returnPressed.connect(self.command_cb)

            self.shell = Shell()
            self.shell.debugObj = self


    def reloadLocalPlugin(self, plname):
        """Reload a Ginga local plugin.

        Parameters
        ----------
        plname: string
                The name of the plugin to be reloaded.

        Returns
        -------
        True

        Notes
        -----
        It is a good idea to close the local plugin that you want to
        reload before trying to reload it.
        """
        self.fv.mm.loadModule(plname)
        for chname in self.fv.get_channelNames():
            chinfo = self.fv.get_channelInfo(chname)
            chinfo.opmon.reloadPlugin(plname, chinfo=chinfo)
        return True
            
    def reloadGlobalPlugin(self, plname):
        """Reload a Ginga global plugin.

        Parameters
        ----------
        plname: string
                The name of the plugin to be reloaded.

        Returns
        -------
        True

        Notes
        -----
        Will try to destroy the widget of the global plugin and
        reinstantiate it.
        """
        gpmon = self.fv.gpmon
        pInfo = gpmon.getPluginInfo(plname)
        gpmon.stop_plugin(pInfo)
        self.fv.update_pending(0.5)
        self.fv.mm.loadModule(plname)
        gpmon.reloadPlugin(plname)
        self.fv.start_global_plugin(plname)
        return True

    def write(self, outputstr):
        output = outputstr.split('\n')
        self.history.extend(output)
        
        # Remove all history past history size
        self.history = self.history[-self.histmax:]
        # Update text widget
        self.tw.setText('\n'.join(self.history))

    def command(self, cmdstr):
        # Evaluate command
        try:
            result = eval(cmdstr)

        except Exception, e:
            result = str(e)
            # TODO: add traceback

        # Append command to history
        self.write('>>> ' + cmdstr + '\n')
        # Write result
        self.write(str(result))

    def command(self, cmdstr):
        # Evaluate command
        self.shell.push(cmdstr)

        
    def command_cb(self):
        w = self.entry
        # TODO: implement a readline editing widget
        cmdstr = str(w.text()).strip()
        self.command(cmdstr)
        w.setText("")
        
    def event_loop(self, kernel):
        kernel.timer = QtCore.QTimer()
        kernel.timer.timeout.connect(kernel.do_one_iteration)
        kernel.timer.start(1000*kernel._poll_interval)

    def default_kernel_app(self):
        app = IPKernelApp.instance()
        app.initialize(['python', '--pylab=qt'])
        app.kernel.eventloop = self.event_loop
        return app

    def default_manager(self, kernel):
        connection_file = find_connection_file(kernel.connection_file)
        manager = QtKernelManager(connection_file=connection_file)
        manager.load_connection_file()
        manager.start_channels()
        atexit.register(manager.cleanup_connection_file)
        return manager

    def console_widget(self, manager):
        try: # Ipython v0.13
            widget = RichIPythonWidget(gui_completion='droplist')
        except TraitError:  # IPython v0.12
            widget = RichIPythonWidget(gui_completion=True)
        widget.kernel_manager = manager
        return widget

    def terminal_widget(self):
        self.kernel_app = self.default_kernel_app()
        manager = self.default_manager(self.kernel_app)
        widget = self.console_widget(manager)

        #update namespace
        self.kernel_app.shell.user_ns.update(self.namespace)

        self.kernel_app.start()
        return widget

    def __str__(self):
        return 'debug'
    
#END
