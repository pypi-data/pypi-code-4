"""
Copyright (c) 2013 John Vrbanac

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from types import FunctionType, MethodType

from pyevents.event import Listener


class EventDispatcher(object):

    def __init__(self):
        super(EventDispatcher, self).__init__()
        self.listeners = []

    def add_listener(self, event_name, callback):
        call_type = type(callback)
        if type(event_name) is not str:
            raise TypeError('event_name has to be a string')
        if call_type is not FunctionType and call_type is not MethodType:
            raise TypeError('callback has to be a function or method')

        listener = Listener(event_name, callback)
        self.listeners.append(listener)
        return listener

    def has_listener(self, event_name, callback):
        contains = [listener for listener in self.listeners
                    if listener.event_name == event_name]
        return len(contains) > 0

    def remove_listener(self, event_name, callback):
        if self.has_listener(event_name, callback):
            self.listeners.remove(Listener(event_name, callback))

    def dispatch(self, event):
        to_call = [l for l in self.listeners if l.event_name == event.name]
        for listener in to_call:
            callback_type = type(listener.callback)
            if callback_type is FunctionType or callback_type is MethodType:
                listener.callback(event)
