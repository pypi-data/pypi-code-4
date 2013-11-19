import os


class Tape (object):
    def __init__(self):
        self.name = '00000'
        self.extras = '0'


class TapeGroup (object):
    def __init__(self):
        self.id = None
        self.name = 'New Group'
        self.tapes = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class TapeGroupBackend (object):
    def __init__(self):
        self.groups = []
        self.root = '/var/lib/syslink/archive/tapegroups'

    def reload(self):
        self.groups = []
        for f in os.listdir(self.root):
            lines = open(os.path.join(self.root, f)).read().splitlines()
            g = TapeGroup()
            g.id = f
            g.name = lines[0]
            for l in lines[1:]:
                t = Tape()
                t.name, t.extras = l.split(',', 1)
                g.tapes.append(t)
            self.groups.append(g)

        for g in self.groups:
            if g.id == 'blank':
                break
        else:
            g = TapeGroup()
            g.id = 'blank'
            g.name = 'blank'
            self.groups.append(g)
            self.save()

    def save(self):
        for f in os.listdir(self.root):
            os.unlink(os.path.join(self.root, f))

        for g in self.groups:
            if not g.id:
                id = 0
                for f in os.listdir(self.root):
                    if not '.' in f:
                        if f != 'blank' and int(f) >= id:
                            id = int(f) + 1
                g.id = str(id)

            c = ''.join((tape.name + ',' + tape.extras + '\n') for tape in g.tapes)
            c = g.name + '\n' + c
            open(os.path.join(self.root, g.id), 'w').write(c)
