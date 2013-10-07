import re
import sys
import traceback


class InteractiveCommand(object):
    def __init__(self, shell=None):
        self.shell = shell

    def get_options(self):
        return {}

    def get_name(self):
        raise NotImplementedError, 'Must implement'

    def handle_command(self):
        raise NotImplementedError, 'Must implement'

    def get_short_description(self):
        raise NotImplementedError, 'Must implement'


class InteractiveShell(object):

    class _HelpCommand(InteractiveCommand):
        """
        Prints a list of available commands and their descriptions, or the help
        text of a specific command. Requires a list of the available commands in
        order to display text for them. 
        
        @ivar commands: A dictionary of available commands, bound to L{InteractiveShell.commands}
        @type commands: C{dict}
        """
        def __init__(self, commands):
            """
            Constructor function for L{_HelpCommand}.
            
            @param commands: A dictionary of available commands, usually L{InteractiveShell.commands}
            @type commands: C{dict}
            """
            self.commands = commands

        def get_name(self):
            return 'help'
    
        def get_options(self):
            return { }

        def handle_command(self, opts, args):
            """
            Prints a list of available commands and their descriptions if no
            argument is provided. Otherwise, prints the help text of the named
            argument that represents a command. Does not throw an error if the
            named argument doesn't exist in commands, simply prints a warning.
            
            @param opts: Will be an empty dictionary
            @type opts: C{dict}
            @param args: The raw string passed to the command, either a command or nothing
            @type args: C{list}
            
            @return: Returns nothing, sends messages to stdout
            @rtype: None
            """
            
            if len(args) == 0:
                self.do_command_summary( )
                return

            if args[0] not in self.commands:
                print 'No help available for unknown command "%s"' % args[0]
                return
            
            print self.commands[args[0]].get_help_message( )
            

        def do_command_summary(self):
            """
            If no command is given to display help text for specifically, then
            this helper method is called to print out a list of the available
            commands and their descriptions. Iterates over the list of commands,
            and gets their summary from L{InteractiveCommand.get_short_description}
            
            @return: Returns nothing, sends messages to stdout
            @rtype: C{None}
            """
            print 'The following commands are available:\n'

            cmdwidth = 0
            for name in self.commands.keys( ):
                if len(name) > cmdwidth:
                    cmdwidth = len(name)

            cmdwidth += 2
            for name in sorted(self.commands.keys( )):
                command = self.commands[name]

                if name == 'help':
                    continue
                
                print '  %s   %s' % (name.ljust(cmdwidth),
                                     command.get_short_description( ))
                

        def get_short_description(self):
            return ''
    
        def get_help_message(self):
            return ''

    class _ExitCommand(InteractiveCommand):
        """
        Exits the interactive shell. 
        """
        def get_name(self):
            return 'exit'

        def get_options(self):
            return { }

        def handle_command(self, opts, args):
            sys.exit(0)

        def get_short_description(self):
            return 'Exit the program.'
    
        def get_help_message(self):
            return 'Type exit and the program will exit.  There are no options to this command'

    def __init__(self, 
                 banner="Welcome to Interactive Shell",
                 prompt=" >>> "):
        self.banner = banner
        self.prompt = prompt
        self.commands = { }
        self.add_command(self._HelpCommand(self.commands))
        self.add_command(self._ExitCommand())

    def add_command(self, command):
        if command.get_name( ) in self.commands:
            raise Exception, 'command %s already registered' % command.get_name( )

        self.commands[command.get_name()] = command

    def handle_input(self, command_line):

        command_line = command_line.strip()

        # Get command
        command_args = ""
        if " " in command_line:
            command_line_index = command_line.index(" ")
            command_name = command_line[:command_line_index]
            command_args = command_line[command_line_index+1:]
        else:
            command_name = command_line

        # Show message when no command
        if not command_name in self.commands:
            print 'Unknown command: "%s". Type "help" for a list of commands.' % command_name
            return

        command = self.commands[command_name]

        opts = {}
        args = []

        # Split the input to allow for quotes option values
        re_args = re.findall('\-\-\S+\=\"[^\"]*\"|\S+', command_args)
        # Parse args if present
        for i in xrange(0, len(re_args)):
            args.append( re_args[i] )

        try:
            command.handle_command(opts=opts, args=args)
        except Exception as err:
            print "Exception occurred while processing command."
            traceback.print_exc( )

    def run(self):
        print self.banner
        print
        print 'Type "help" at any time for a list of commands.'

        while True:
            try:
                print
                command_line = raw_input(self.prompt)
            except (KeyboardInterrupt, EOFError):
                break

            self.handle_input(command_line)
