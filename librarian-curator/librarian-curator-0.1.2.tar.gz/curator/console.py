"""Console super class for a Command Line Interface."""
from __future__ import print_function
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
import cmd
try:
    import readline
except ImportError:
    readline = None


class Console(cmd.Cmd):
    """Console is a CLI component based on the cmd module."""
    def __init__(self):
        """
        Takes a filename for the database and will create it and any required
        tables if the database filename doesnt exist.
        """
        cmd.Cmd.__init__(self)
        self.prompt = "=>> "
        if readline is None:
            self.completekey = None

    def do_hist(self, _):
        """Print a list of commands that have been entered"""
        print(self._hist)

    def do_exit(self, _):
        """Exits from the console"""
        return -1

    def do_help(self, args):
        """
        Get help on commands
        'help' or '?' with no arguments prints a list of commands for which
        help is available 'help <command>' or '? <command>' gives help on
        <command>
        """
        cmd.Cmd.do_help(self, args)

    def preloop(self):
        """
        Initialization before prompting user for commands. Despite the claims
        in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)
        self._hist = []

    def postloop(self):
        """Take care of any unfinished business."""
        cmd.Cmd.postloop(self)

    def precmd(self, line):
        """
        Called after a line has been input but before it has been interpreted.
        """
        self._hist.append(line.strip())
        return line

    def postcmd(self, stop, line):
        """
        If you want to stop the console, return something that evaluates to
        true. If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        self.do_help(None)

    def default(self, line):
        """
        Called on an input line when the command prefix is not recognized.
        In that case we execute the line as Python code.
        """
        self.do_help(None)
