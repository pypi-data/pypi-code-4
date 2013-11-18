from mercurial import ui

class mscui(ui.ui):
    """ inhibit stdout output and
    keep the last output around.
    Handy when test-debugging ...
    """
    def __init__(self, *args):
        super(mscui, self).__init__(*args)
        self.setconfig('ui', 'interactive', 'false')
        self.setconfig('ui', 'ssh', 'ssh -o BatchMode=yes -o IdentitiesOnly=yes')
        self.pushbuffer()
