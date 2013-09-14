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


class Event(object):

    def __init__(self, event_name, payload=None):
        super(Event, self).__init__()
        self.name = event_name
        self.payload = payload

    def __eq__(self, other):
        result = False
        if isinstance(other, Event):
            result = (self.name == other.name and
                      self.payload == other.payload)
        return result


class Listener(object):

    def __init__(self, event_name, callback):
        super(Listener, self).__init__()
        self.event_name = event_name
        self.callback = callback

    def __eq__(self, other):
        result = False
        if type(other) is Listener:
            result = (self.event_name == other.event_name and
                      self.callback == other.callback)
        return result

    def __ne__(self, other):
        return not self.__eq__(other)
