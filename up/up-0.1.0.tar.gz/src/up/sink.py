from pymongo import MongoClient
from up.util import NAME_SEPARATOR, colors
from up.moods import moods


class StatusSink(object):

    def process_status(self, status, deep=0, surname=''):
        raise NotImplemented

    def add_annotation(self, note):
        raise NotImplemented

    def set_mood(self, mood):
        """
        The mood of any messaging.
        """
        self.mood = mood

    def set_verbosity(self, verbosity):
        """
        If the sink outputs to stdout, use this value to control the amount of
        output.
        """
        self.verbosity = verbosity

    def set_status(self, source, deep=0, surname=''):
        self.process_status(source, deep, surname)

        # duck type a StatusTreeSource, not to be confused with TreeStatusSink
        if hasattr(source, 'children'):
            for status in source.children:
                self.set_status(status, deep + 1, surname + NAME_SEPARATOR + source.name)


class TreeStatusSink(StatusSink):
    def __init__(self, children):
        super(TreeStatusSink, self).__init__()
        self.children = children

    def add_annotation(self, note):
        for child in self.children:
            child.add_annotation(note)

    def set_mood(self, mood):
        for child in self.children:
            child.set_mood(mood)

    def set_verbosity(self, verbosity):
        for child in self.children:
            child.set_verbosity(verbosity)

    def set_status(self, source):
        for child in self.children:
            child.set_status(source)


class MongoStatusSink(StatusSink):
    DB_NAME = 'up'

    def __init__(self, domain, port):
        super(MongoStatusSink, self).__init__()
        client = MongoClient(domain, port)
        self.db = client[self.DB_NAME]

    def add_annotation(self, note):
        self.db.annotations.insert(note.__dict__)

    def process_status(self, status, deep=0, surname=''):
        self.db.statuses.insert({
            'path': surname + NAME_SEPARATOR + status.name,
            'up': status.status,
            'date': status.date,
            'duration': status.duration
        })


class StdOutStatusSink(StatusSink):

    messages = {
        moods.REALIST: [
            colors.FAIL + 'DOWN' + colors.END,
            colors.FAIL + 'MOSTLY DOWN' + colors.END,
            colors.WARNING + 'HALF UP' + colors.END,
            colors.WARNING + 'MOSTLY UP' + colors.END,
            colors.OK + 'UP' + colors.END
        ],
        moods.OPTIMIST: [
            colors.FAIL + 'HANG IN THERE!' + colors.END,
            colors.FAIL + 'SLIGHTLY UP' + colors.END,
            colors.WARNING + 'HALF UP' + colors.END,
            colors.WARNING + 'MOSTLY UP' + colors.END,
            colors.OK + 'UP' + colors.END
        ],
        moods.PESSIMIST: [
            colors.FAIL + 'GET TO WORK!' + colors.END,
            colors.FAIL + 'MOSTLY DOWN' + colors.END,
            colors.WARNING + 'HALF DOWN' + colors.END,
            colors.WARNING + 'SLIGHTLY DOWN' + colors.END,
            colors.OK + 'WHATEVER' + colors.END
        ]
    }

    def add_annotation(self, note):
        print(colors.PARENTHETICAL + note.message + colors.END + '\n')

    def process_status(self, status, deep=0, surname=''):
        # stop outputting if we've passed the verbosity setting.
        if deep > self.verbosity:
            return

        messages = self.messages[self.mood]
        message = int(status.status * (len(messages) - 1))

        print(('  ' * deep) + status.name + ': ', end='')
        #print(message, end='')
        print(messages[message], end='')

        if status.status < 1 and status.status > 0:
            print(colors.PARENTHETICAL + ' ({percent:.4}%)'.format(percent=float(status.status) * 100) + colors.END, end='')

        if status.date is not None and status.duration > 1E-4:
            print(colors.PARENTHETICAL + ' ({duration:.4}s)'.format(duration=status.duration) + colors.END)
        else:
            print()
