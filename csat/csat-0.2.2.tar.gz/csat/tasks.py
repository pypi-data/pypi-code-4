import uuid
import json
import os

from collections import OrderedDict


class TaskManager(object):
    def __init__(self):
        self.tasks = []
        self.event_handlers = {}

    def new(self, *args, **kwargs):
        task = Task(*args, **kwargs)
        self.register(task)
        return task

    def register(self, task):
        self.tasks.append(task)
        self.task_updated(task)
        canc = task.observe(self.task_updated)
        self.event_handlers[task.uuid] = canc

    def unregister(self, task):
        self.tasks.remove(task)
        self.event_handlers.pop(task.uuid)()

    def task_updated(self, task):
        pass


class VT100Terminal(object):
    def __init__(self, stream):
        self.stream = stream
        self._lines = 0
        self._position = -1

    def writenl(self, line=''):
        self._lines += 1
        self.write(line + '\n')

    def write(self, s):
        self.stream.write(s)
        self._position = self.stream.tell()

    def clearline(self):
        self.write(chr(27) + "[2K")

    def size(self):
        env = os.environ

        def ioctl_GWINSZ(fd):
            try:
                import fcntl
                import termios
                import struct
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                     '1234'))
            except:
                return
            return cr

        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)

        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass

        if not cr:
            cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        return int(cr[1]), int(cr[0])

    def width(self):
        return self.size()[0]

    def reset(self):
        if self._position == self.stream.tell():
            if self._lines:
                self.write(chr(27) + '[{}A'.format(self._lines))
        self._lines = 0


class ConsoleTaskManager(TaskManager):
    width = 100
    name_width = 25
    status_width = 9

    def __init__(self, terminal, pretty=True):
        super(ConsoleTaskManager, self).__init__()
        self.terminal = terminal
        self.pretty = pretty

    def task_updated(self, task):
        if self.pretty:
            self.terminal.reset()
            self.terminal.writenl()

        terminal_width = self.terminal.width()
        bar_width = (min(self.width, terminal_width)
                     - self.name_width
                     - 2  # Name - Bar separator
                     - 1  # Bar - Percentage separator
                     - 6  # Percentage
                     - 3  # Percentage - Status separator
                     - self.status_width)

        for task in self.tasks:
            self.terminal.clearline()
            status = task.statusName

            if task.progress == task.INDEFINITE:
                bar = '-' * bar_width
                percent = '     ?'
            else:
                ticks = int(bar_width * task.progress)
                bar = '#' * ticks + '.' * (bar_width - ticks)
                percent = '{:5.1f}%'.format(task.progress * 100)

            if bar_width < 0:
                    text = (
                        '{:>{name_width}}: {} - {:{status_width}s}'.format(
                            task.name,
                            percent,
                            status.capitalize(),
                            name_width=self.name_width,
                            status_width=self.status_width,
                        )
                    )
            else:
                text = ('{:>{name_width}}: {:{bar_width}s} {} - '
                        '{:{status_width}s} - {}'.format(
                            task.name,
                            bar,
                            percent,
                            status.capitalize(),
                            task.statusText,
                            name_width=self.name_width,
                            bar_width=bar_width,
                            status_width=self.status_width,
                        ))
            self.terminal.writenl(text[:terminal_width])
        if self.pretty:
            self.terminal.writenl()


class JsonRPCTaskManager(TaskManager):
    def __init__(self, stream):
        super(JsonRPCTaskManager, self).__init__()
        self.stream = stream

    def task_updated(self, task):
        self.stream.write(json.dumps({
            'method': 'updateTask',
            'params': [
                self.tasks.index(task),
                task.getState()
            ],
        }) + '\n')


class Task(object):
    """
    A simple object representing a task.
    """

    INACTIVE = 0
    RUNNING = 1
    PAUSED = 2
    COMPLETED = 3
    FAILED = 4
    INDEFINITE = -1

    STATUS_NAMES = {
        INACTIVE: 'waiting',
        RUNNING: 'running',
        PAUSED: 'paused',
        COMPLETED: 'completed',
        FAILED: 'failed',
        INDEFINITE: 'indefinite',
    }

    updateProgressThreshold = 0.01  # Only send updates each 1%

    def __init__(self, name, unique_id=None):
        self.eventHandlers = OrderedDict()
        self.name = name
        self.uuid = unique_id or str(uuid.uuid4())
        self._status = self.INACTIVE
        self._steps = self.INDEFINITE
        self._totalSteps = 1
        self._statusText = 'Waiting to start...'
        self._progress = self.INDEFINITE
        self._oldProgress = self._progress

    def observe(self, func):
        key = object()
        self.eventHandlers[key] = func
        return lambda: self.eventHandlers.pop(key, None)

    def _updated(self):
        for handler in self.eventHandlers.itervalues():
            handler(self)

    @property
    def statusName(self):
        return self.STATUS_NAMES[self._status]

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, val):
        self._status = val
        self._updated()

    @property
    def statusText(self):
        return self._statusText

    @statusText.setter
    def statusText(self, val):
        self._statusText = val
        self._updated()

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, val):
        self._progress = val
        diff = abs(self._progress - self._oldProgress)

        if diff > self.updateProgressThreshold:
            self._updated()
            self._oldProgress = self._progress

    @property
    def steps(self):
        return self._totalSteps

    @steps.setter
    def steps(self, val):
        if self._steps == self.INDEFINITE:
            self._steps = 0
        self._totalSteps = val
        self._progress = self._steps / self._totalSteps

    def setIndefinite(self):
        self._steps = self.INDEFINITE
        self._progress = self.INDEFINITE

    def setCompleted(self):
        """
        Mark this task as completed.
        """
        self._status = self.COMPLETED
        self._progress = 1
        self._statusText = 'Done.'
        if self._totalSteps != self.INDEFINITE:
            self._steps = self._totalSteps
        self._updated()

    def makeStep(self, steps=1):
        if self._totalSteps == self.INDEFINITE:
            raise RuntimeError('Cannot make a step if the total number of '
                               'steps is not defined.')
        self._status = self.RUNNING
        self._steps += steps
        self.progress = self._steps * 1.0 / self._totalSteps

    def getState(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'status': self.status,
            'statusText': self.statusText,
            'progress': self.progress,
        }

    def updateState(self, state):
        assert state['uuid'] == self.uuid

        self._status = state['status']
        self._statusText = state['statusText']
        self._progress = state['progress']
        self._updated()

    @classmethod
    def fromState(cls, state):
        task = cls(state['name'], state['uuid'])
        task._status = state['status']
        task._statusText = state['statusText']
        task._progress = state['progress']
        return task
