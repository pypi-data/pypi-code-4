import curses, time, datetime
from gadgets.ui.window import Window

class Notes(Window):
    """notes"""

    _table = '''CREATE TABLE if not exists notes
             (host text, method_id integer, timestamp integer, notes text)'''

    _insert = '''INSERT INTO notes VALUES(?, ?, ?, ?)'''
    _notes_query = '''SELECT * FROM notes WHERE host = ? ORDER BY timestamp DESC LIMIT 10'''

    def __init__(self, socket, lock, db):
        self._name = None
        self._socket = socket
        self._lock = lock
        db.ensure_table(self._table)
        self._db = db
        self._width = 40
        self._height = 18

    def _save(self, notes, method_id):
        timestamp=datetime.datetime.now()
        self._db.save(self._insert, (self._name, method_id, int(timestamp.strftime('%s')), notes))

    def _new_note(self, screen, method_id):
        win = self._get_subwin(screen)
        self._add_title(win, self.__doc__)
        curses.echo()
        curses.curs_set(1)
        note = ''
        row = 2
        while not note.endswith('\n\n'):
            win.move(row ,1)
            note += win.getstr() + '\n'
            row += 1
        curses.noecho()
        curses.curs_set(0)
        if note != '':
            note = note.strip()
            self._save(note, method_id)

    def _show_note(self, x, notes, screen):
        try:
            i = int(chr(x)) - 1
            note = notes[i]
        except IndexError:
            pass
        except ValueError:
            pass
        else:
            lines = note[3].split('\n')
            win = self._get_subwin(screen)
            self._add_title(win, self.__doc__)
            row = 2
            for line in lines:
                win.addstr(row, 2, line)
                row += 1
            win.getch()

    def _show_notes(self, screen, win, method_id):
        notes = [note for note in self._db.query(self._notes_query, [self._name])]
        row = 2
        for i, note in enumerate(notes):
            d = datetime.datetime.fromtimestamp(note[2])
            win.addstr(row, 2, '{0}: {1}'.format(i + 1, d))
            row += 1
        win.addstr(row, 2, 'n: new note')
        x = win.getch()
        if chr(x) == 'n':
            self._new_note(screen, method_id)
        else:
            self._show_note(x, notes, screen)

    def __call__(self, screen, data, method_id=None, name=None):
        self._name = name
        self._lock.acquire()
        win = self._get_subwin(screen)
        self._add_title(win, self.__doc__)
        self._show_notes(screen, win, method_id)
        self._lock.release()
        
