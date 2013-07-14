import os
import subprocess


class LTFSDrive (object):
    def __init__(self):
        self.drive = ''
        self.status = ''
        self.barcode = ''
        self.origin = ''


class LTFSLibraryBackend (object):
    def __init__(self):
        self.root = '/var/lib/syslink/archive/library'

    def reload(self):
        self.drives = []
        self.mailbox = []
        self.slots = []

        for l in open(self.root + '/drives').read().splitlines():
            d = LTFSDrive()
            tokens = [_.strip() for _ in l.split(':')]
            d.drive = tokens[0].split()[3]
            d.status = tokens[1].split()[0]
            if d.status != 'Empty':
                d.origin = tokens[1].split()[3]
                if len(tokens) > 2:
                    d.barcode = tokens[2].split()[2]
            self.drives.append(d)

        for l in open(self.root + '/slots').read().splitlines():
            d = LTFSDrive()
            tokens = [_.strip() for _ in l.split(':')]
            d.drive = tokens[0].split()[2]
            d.status = tokens[1]
            if d.status != 'Empty':
                d.barcode = tokens[2].split('=')[1]
            self.slots.append(d)

        for l in open(self.root + '/mailbox').read().splitlines():
            d = LTFSDrive()
            tokens = [_.strip() for _ in l.split(':')]
            d.drive = tokens[0].split()[2]
            d.status = tokens[1]
            if d.status != 'Empty':
                d.barcode = tokens[2].split('=')[1]
            self.mailbox.append(d)

    def run_action(self, action, *args):
        subprocess.Popen([os.path.join(self.root, '../' + action + '.sh')] + list(args))
