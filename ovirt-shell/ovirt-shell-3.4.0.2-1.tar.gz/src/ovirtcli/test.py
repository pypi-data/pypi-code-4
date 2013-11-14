#
# '''
# Created on Oct 22, 2013
#
# @author: mpastern
# '''
#
import curses


# from ovirtcli.state.finitestatemachine import FiniteStateMachine
# from ovirtcli.state.dfsaevent import DFSAEvent
# from ovirtcli.state.dfsastate import DFSAState
#
# import curses, traceback
#
# class Test(object):
#     '''
#     the test class
#     '''
#     def run(self):
# PColLinux =  coloransi.ColorScheme(
#     'Linux',
#     in_prompt  = InputColors.Green,
#     in_number  = InputColors.LightGreen,
#     in_prompt2 = InputColors.Green,
#     in_normal  = InputColors.Normal,  # color off (usu. Colors.Normal)
#
#     out_prompt = Colors.Red,
#     out_number = Colors.LightRed,
#
#     normal = Colors.Normal
#     )
# #         sm = FiniteStateMachine(
# #             events=[
# #                 DFSAEvent(
# #                   name='disconnect',
# #                   sources=[
# #                        DFSAState.CONNECTED,
# #                        DFSAState.UNAUTHORIZED
# #                   ],
# #                   destination=DFSAState.Disconnected,
# #                   callbacks=[self.onDisconnect]),
# #                 DFSAEvent(
# #                   name='connect',
# #                   sources=[
# #                        DFSAState.Disconnected,
# #                        DFSAState.Unauthorized
# #                   ],
# #                   destination=DFSAState.Connected,
# #                   callbacks=[self.onConnect]),
# #                 DFSAEvent(
# #                   name='unauthorized',
# #                   sources=[
# #                        DFSAState.Connected
# #                   ],
# #                   destination=DFSAState.Unauthorized,
# #                   callbacks=[]),
# #             ]
# #         )
#
# #         sm2 = FiniteStateMachine(
# #             events=[
# #                 DFSAEvent(
# #                   name='disconnect',
# #                   sources=[
# #                        DFSAState.Connected,
# #                        DFSAState.Unauthorized
# #                   ],
# #                   destination=DFSAState.Disconnected,
# #                   callbacks=[self.onDisconnect]),
# #                 DFSAEvent(
# #                   name='connect',
# #                   sources=[
# #                        DFSAState.Disconnected,
# #                        DFSAState.Unauthorized
# #                   ],
# #                   destination=DFSAState.Connected,
# #                   callbacks=[self.onConnect]),
# #                 DFSAEvent(
# #                   name='unauthorized',
# #                   sources=[
# #                        DFSAState.Connected
# #                   ],
# #                   destination=DFSAState.Unauthorized,
# #                   callbacks=[]),
# #             ]
# #         )
# #
# #         print sm is sm2
# #         print id(sm) == id(sm2)
#
# #         sm.connect()
# #         print sm; print "\n"
# #         sm.disconnect()
# #         print sm; print "\n"
# #         sm.unauthorized()
# #         print sm; print "\n"
#
#
# #     def onConnect(self, **kwargs):
# #         print "connect callback with:\n%s\n\n" % kwargs['event']
# #
# #     def onDisconnect(self, **kwargs):
# #         print "disconnect callback:\n%s\n\n" % kwargs['event']
#
# Test().run()
# import curses
# from curses import panel
#
# class Menu(object):
#
#     def __init__(self, items, stdscreen):
#         self.window = stdscreen.subwin(0, 0)
#         self.window.keypad(1)
#         self.panel = panel.new_panel(self.window)
#         self.panel.hide()
#         panel.update_panels()
#
#         self.position = 0
#         self.items = items
#         self.items.append(('exit', 'exit'))
#
#     def navigate(self, n):
#         self.position += n
#         if self.position < 0:
#             self.position = 0
#         elif self.position >= len(self.items):
#             self.position = len(self.items) - 1
#
#     def display(self):
#         self.panel.top()
#         self.panel.show()
#         self.window.clear()
#
#         while True:
#             self.window.refresh()
#             curses.doupdate()
#             for index, item in enumerate(self.items):
#                 if index == self.position:
#                     mode = curses.A_REVERSE
#                 else:
#                     mode = curses.A_NORMAL
#
#                 msg = '%d. %s' % (index, item[0])
#                 self.window.addstr(1 + index, 1, msg, mode)
#
#             key = self.window.getch()
#
#             if key in [curses.KEY_ENTER, ord('\n')]:
#                 if self.position == len(self.items) - 1:
#                     break
#                 else:
#                     self.items[self.position][1]()
#
#             elif key == curses.KEY_UP:
#                 self.navigate(-1)
#
#             elif key == curses.KEY_DOWN:
#                 self.navigate(1)
#
#         self.window.clear()
#         self.panel.hide()
#         panel.update_panels()
#         curses.doupdate()
#
# class MyApp(object):
#
#     def __init__(self, stdscreen):
#         self.screen = stdscreen
#         curses.curs_set(0)
#
#         submenu_items = [
#                 ('beep', curses.beep),
#                 ('flash', curses.flash)
#                 ]
#         submenu = Menu(submenu_items, self.screen)
#
#         main_menu_items = [
#                 ('beep', curses.beep),
#                 ('flash', curses.flash),
#                 ('submenu', submenu.display)
#                 ]c
#         main_menu = Menu(main_menu_items, self.screen)
#         main_menu.display()
#
# if __name__ == '__main__':
#     curses.wrapper(MyApp)

import curses

# initialize curses
stdscr = curses.initscr()
curses.start_color()

# initialize color #1 to Blue with Cyan background
curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_CYAN)

stdscr.addstr('A sword and a shield.', curses.color_pair(1))
stdscr.refresh()

# finalize curses
curses.endwin()
