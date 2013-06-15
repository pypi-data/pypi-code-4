'''
Copyright 2012 Alexey Kravets  <mr.kayrick@gmail.com>

This file is part of PyMind.

PyMind is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyMind is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyMind.  If not, see <http://www.gnu.org/licenses/>.
'''

import curses
import curses.textpad
import locale
import map_print
from mindmeister.ideas import insert, delete, change, move, toggleClosed
from mindmeister.maps import undo as map_undo
from mindmeister.maps import redo as map_redo
from mindmeister.maps import getMap
from mindmeister.diagnostic import MindException

__idea_to_reparent = None

def get_position(win):
  curr_pos = win.getyx()
  while 1:
    win.addstr (curr_pos[0], curr_pos[1], "Position (optional) [x_pos y_pos] >> ")
    win.clrtobot()
    curses.echo()
    result = win.getstr().rstrip()
    curses.noecho()
    if len(result) == 0:
      return None
    pos = result.split()
    if len (pos) != 2:
      win.addstr ("Invalid pos format")
      win.getch()
      continue
    try:
      return map (lambda item: int(item), pos)
    except Exception:
      win.addstr ("Can not parse number")
      win.getch()
      continue

def get_name (win, message, init = ""):
  win.addstr (message)
  win.refresh()
  #curses.echo()
  #result = win.getstr().rstrip()
  #curses.noecho()
  curr_pos = win.getyx ()
  new_win = win.derwin (1, 20, curr_pos[0], curr_pos[1])
  new_win.erase ()
  new_win.addstr (init)
  tb = curses.textpad.Textbox(new_win)
  result = tb.edit().rstrip()
  if len (result) == 0:
    return None
  return result

def print_help (win, map, token, data):
  '''Print help'''
  win.clear ()
  win.addstr (0, 0, "Commands list\n")
  for key,action in __mapping.items():
    win.addstr (chr(key) + " - " + action.__doc__  + '\n')

  win.addstr ('q' + " - " + 'quit'  + '\n')
  win.addstr ('CTLR+C' + " - " + 'break current operation'  + '\n')
  win.addstr ('Up' + " - " + 'go to the previous idea'  + '\n')
  win.addstr ('Down' + " - " + 'go to the next idea'  + '\n')
  win.addstr ('Right' + " - " + 'go to the first child idea'  + '\n')
  win.addstr ('Right' + " - " + 'go to the parent idea'  + '\n')
  win.refresh ()
  win.getch ()
  return False

def add_node (win, map, idea, token):
  '''Add new idea to map'''
  name = get_name (win, "New idea name:", "new idea")
  if name == None:
    return False
  pos = get_position (win)
  if pos != None:
    args = {'x_pos' : pos[0], 'y_pos' : pos [1]}
  else:
    args = {}
  insert (token, map.map.id, idea.id, name, **args)
  return True

def delete_node (win, map, idea, token):
  '''Delete current idea'''
  delete (token, idea.id, map.map.id)
  return True

def edit_node (win, map, idea, token):
  '''Edit current idea (change its title)'''
  name = get_name (win, "Idea title:", idea.title)
  if name == None:
    return False
  change (token, idea.id, map.map.id, title = name)
  return True

def reparent_node (win, map, idea, token):
  '''Move current idea to another parent'''
  global __idea_to_reparent
  if __idea_to_reparent == None:
    __idea_to_reparent = idea
    return False
  move (token, __idea_to_reparent.id, map.map.id, idea.id, 0)
  __idea_to_reparent = None
  return True

def undo (win, map, idea, token):
  '''Undo'''
  map_undo (token, map.map.id)
  return True

def redo (win, map, idea, token):
  '''Redo'''
  map_redo (token, map.map.id)
  return True

def info (win, map, idea, token):
  '''Show detailed info for the current idea'''
  win.clear ()
  win.addstr (0, 0, idea.title + "\n\n")
  win.addstr ("Modification date: " + str(idea.modifiedat) + "\n")
  win.addstr ("Rank: " + str(idea.rank) + "\n")
  win.addstr ("Is Closed: " + str(idea.closed) + "\n")
  win.refresh ()
  win.getch ()
  return False

def toggle (win, map, idea, token):
  '''Toggle the open/closed status of the current idea'''
  toggleClosed (token, idea.id, map.map.id)
  return True

def next_priority (icon):
  if not icon.startswith ("priority_"):
    return None
  return "priority_" + str (int (icon[len("priority_"):]) % 10 + 1)

def next_task (icon):
  if not icon.startswith ("task_"):
    return None
  return "task_" + str (int (icon[len("task_"):]) % 5 + 1)

def modify_priority (win, map, idea, token):
  '''Modify the priority of the current idea'''
  for index,icon in enumerate (idea.icons):
    new_icon = next_priority (icon)
    if new_icon != None:
      idea.icons [index] = new_icon
      break
  else:
    idea.icons.append ("priority_01")

  new_icons = ",".join (idea.icons)
  change (token, idea.id, map.map.id, icon = new_icons)

  return True

def modify_status (win, map, idea, token):
  '''Modify the status of the current idea'''
  for index,icon in enumerate (idea.icons):
    new_icon = next_task (icon)
    if new_icon != None:
      idea.icons [index] = new_icon
      break
  else:
    idea.icons.append ("task_01")

  new_icons = ",".join (idea.icons)
  change (token, idea.id, map.map.id, icon = new_icons)

  return True

def clear_priority (win, map, idea, token):
  '''Clear the priority of the current idea'''
  for index,icon in enumerate (idea.icons):
    if icon.startswith ("priority_"):
      idea.icons.pop(index)
      break
  else:
    return False

  new_icons = ",".join (idea.icons)
  change (token, idea.id, map.map.id, icon = new_icons)

  return True

def clear_status (win, map, idea, token):
  '''Clear the status of the current idea'''
  for index,icon in enumerate (idea.icons):
    if icon.startswith ("task_"):
      idea.icons.pop(index)
      break
  else:
    return False

  new_icons = ",".join (idea.icons)
  change (token, idea.id, map.map.id, icon = new_icons)

  return True

__mapping = {
    ord('h') : print_help,\
    ord('a') : add_node,\
    ord('d') : delete_node,\
    ord('e') : edit_node,\
    ord('r'): reparent_node,\
    ord('u') : undo,\
    ord('i') : info,\
    ord('t') : toggle,\
    ord('p') : modify_priority,\
    ord('s') : modify_status,\
    ord('P') : clear_priority,\
    ord('S') : clear_status,\
    ord('y') : redo}

def update_map (map, token):
  new = getMap (token, map.map.id)
  map.map = new.map
  map.ideas = new.ideas

def edit_map (map, token):
  global __idea_to_reparent
  locale.setlocale(locale.LC_ALL,"")
  stdscr = curses.initscr()
  curses.noecho()
  stdscr.keypad(1)
  curses.cbreak()

  index = [0]
  curr = map.ideas[index[-1]]

  try:
    while 1:
      try:
        stdscr.clear()
        map_print.print_curses (map, stdscr, curr)
        if __idea_to_reparent != None:
          stdscr.addstr("\nPlease select new parent and press 'r'")

        cmd = stdscr.getch()
        if cmd == ord('q'):
          break

        if cmd == curses.KEY_LEFT:
          if curr.parent:
            curr = curr.int_parent
            index.pop()
          continue

        if cmd == curses.KEY_RIGHT:
          if curr.closed == "false" and len(curr.ideas) > 0:
            curr = curr.ideas[0]
            index.append (0)
          continue

        if cmd == curses.KEY_UP:
          if curr.int_parent and index[-1] > 0:
            index[-1] -= 1
            curr = curr.int_parent.ideas [index[-1]]
          continue

        if cmd == curses.KEY_DOWN:
          if curr.int_parent and index[-1] + 1 < len(curr.int_parent.ideas):
            index[-1] += 1
            curr = curr.int_parent.ideas [index[-1]]
          continue

        if __idea_to_reparent != None:
          if cmd != ord('r'):
            continue

        if not __mapping.has_key (cmd):
          stdscr.addstr("\nInvalid command, use 'h' to obtain the list of the available commands")
          stdscr.getch()
          continue
        if __mapping[cmd](stdscr, map, curr, token):
          update_map (map, token)
          last = index.pop()
          curr = reduce (lambda idea, offset: idea.ideas[offset], index, map)
          if last < len (curr.ideas):
            index.append (last)
            curr = curr.ideas[last]

      except MindException as err:
        stdscr.addstr (str(err))
        stdscr.getch ()
      except KeyboardInterrupt:
        pass
      stdscr.clear ()
  except EOFError:
    pass
  finally:
    curses.echo()
    curses.endwin()
