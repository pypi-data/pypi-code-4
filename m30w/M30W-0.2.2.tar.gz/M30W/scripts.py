# This file is part of the M30W software.
# Copyright (C) 2012-2013 M30W developers.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from weakref import proxy
from pprint import pformat
import types
from M30W.debug import ensure_kurt
try:
    import kurt
except ImportError:
    kurt = None


class Script:
    """A Script stores a list of blocks or scripts.

    A Script is an container that supports parallel threads running. Call to
    Script's ``__iter__()`` method will return a :class:`RunningScript` object.

    In order to make the Script interface more similar to the :class:`Block`
    interface, you may use ``__call__`` as a synonym to ``__iter__`` like
    generators.

    A Script also supports indexing.
    """

    def __init__(self, blocks):
        self.blocks = blocks
        "A list of :class:`Block` or :class:`Script` objects."

    def __iter__(self):
        return RunningScript(self)

    __call__ = __iter__

    def __repr__(self):
        return "<Script%s/>" % pformat(self.blocks)

    def __len__(self):
        return len(self.blocks)

    def __getitem__(self, key):
        return self.blocks[key]

    def __setitem__(self, key, value):
        self.blocks[key] = value

    def __delitem__(self, key):
        del self.blocks[key]

    @classmethod
    def from_kurt(cls, morph, parent):
        ensure_kurt()

        event = None
        if morph[0].command == 'EventHatMorph':
            event = morph.pop(0).args[0].lower()
        elif morph[0].command == 'MouseClickEventHatMorph':
            morph.pop(0)  # TODO: Handle 'When % is clicked
        elif morph[0].command == 'KeyEventHatMorph':
            morph.pop(0)  # TODO: Handle 'When % is pressed' 

        return event, cls.from_list(morph[:], parent)

    @classmethod
    def from_list(cls, l, parent):
        blocks = map(lambda b: Block.from_kurt(b, parent), l)
        return cls(blocks)

class RunningScript:
    """A running script. Will yield results until the script is terminated.
    """

    def __init__(self, script):
        self.script = proxy(script)
        "The :class:`Script` object that is run. Automatically weakrefed."

        self._counter = -1
        self.current_block = None

    def __iter__(self):
        return self

    def next(self):
        if isinstance(self.current_block, types.GeneratorType):
            try:
                next(self.current_block)
            except StopIteration:
                self.current_block = None
        else:
            self._counter += 1
            try:
                self.current_block = self.script[self._counter]()
            except IndexError:
                raise StopIteration


class SpriteNotResolved(SyntaxError): pass


class Block:
    """A Block is a representation of Scratch's command and reporter blocks, as
    well as predicates. It stores a weakref to the sprite, the command token
    ('insert:at:of:List', 'list:contains:'), as well as the block's arguments.
    
    A Block is a callable that returns a generator object or a value, depends on
    the block's type.
    """

    def __init__(self, sprite, command, arguments):
        self.command = command
        "String representing the command being executed."

        self.arguments = arguments
        "A list containing the block's arguments."

        self._sprite = proxy(sprite)

    def __call__(self):
        value = getattr(self.sprite, self.command)(*self.arguments)
        return value

    def __repr__(self):
        return "<Block(%s, %s)/>" % (self.command, pformat(self.arguments)[1:-1])

    @classmethod
    def from_kurt(cls, morph, parent):
        ensure_kurt()
        command = morph.command

        args = morph.args[:]
        for index, arg in enumerate(args):
            if isinstance(arg, list):
                args[index] = Script.from_list(arg, parent)
            if isinstance(arg, kurt.Block):
                args[index] = Block.from_kurt(arg, parent)
            if isinstance(arg, kurt.SpriteRef):
                from M30W.runtime import project
                try:
                    args[index] = project[arg.name]
                except ValueError:
                    raise SpriteNotResolved("Inexistent Sprite %s referred"
                                            % arg.name)

        #Special case for variable blocks :/
        if command == 'changeVariable':
            command = morph.args.pop(1).value

        return cls(parent, command, args)

    @property
    def sprite(self):
        """The :class:`Base` object that owns this block.
        Automatically weakrefed.
        """
        return self._sprite

    @sprite.setter
    def sprite(self, value):
        self._sprite = proxy(value)


class StopScriptsExecution(Exception): pass


class StopScript(Exception): pass


class Engine:
    """The Engine object handles the execution of scripts.
    
    An Engine stores a dictionary of events and scripts that correspond to them,
    thus allowing a broadcasting/event triggering system.
    """
    GREENFLAG_EVENT = 'scratch-startclicked'
    "Constant for the Scratch-StartClicked event."

    def __init__(self):
        self.events = {}
        "Stores event names with scripts that are triggered by those events."

        self.running_scripts = []
        "List of scripts that are being run"

        self.redraw = False
        "Indicates whether the stage should be refreshed before continuing."

    def bind(self, event, script):
        """Bind a script to a specific event.
        
        The script will be executed when the event will be triggered.
        """
        if event in self.events:
            self.events[event].append(script)
        else:
            self.events[event] = [script]

    def trigger(self, event):
        """Trigger an event and execute scripts that are bound to it.
        """
        self.running_scripts.extend(map(iter, self.events.get(event, [])))

    def clear_bindings(self):
        """Clear all event bindings. 
        """
        self.events = {}

    def force_redraw(self):
        """Force redraw of the stage before executing the next block.
        """
        self.redraw = True

    def start(self, event=GREENFLAG_EVENT):
        """Start the execution of scripts and trigger ``event``.

        The `event` parameter indicates what event should be triggered to start
        executing.
        """
        del self.running_scripts[:]
        self.trigger(event)
        self.running = True

        while self.running:
            for script in self.running_scripts:
                try:
                    next(script)
                except (StopScript, StopIteration):
                    self.running_scripts.remove(script)
                    if not self.running_scripts:
                        self.running = False
                except StopScriptsExecution:
                    self.running = False

    def stop(self):
        self.running = False
