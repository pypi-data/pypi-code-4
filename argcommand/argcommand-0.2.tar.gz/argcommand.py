"""
A Python module that provides simple object-oriented abstraction layer for creating command-line interfaces.  

Read README.md for usage documentation
"""

## 
## argcommand
## https://github.com/avinoamr/argcommand
## 
## This module was orginally developed at Win (win.com) by:
##  Roi Avinoam <avinoamr@gmail.com>
##  Oran Ben Zur <oranb83@gmail.com>
##  Nir Naor <nirnaori@gmail.com>
##
##
## The MIT License
## 
## Copyright (c) 2012-2013 argcommand authors
## 
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.
import argparse
import inspect

__version__ = "0.2"

##
class Command( object ):
    """
    The Command class represents a single CLI command
    """

    # list of Command classes that should be included in this Command
    subcommands = []

    # abstract method, needs to be implemented by the concrete Command classes
    def run( self ):
        raise NotImplementedError

    # 
    def __init__( self, cli_args = None, **kargs ):
        """
        Command constructor, replaces the instance's arguments with their values. You should never instantiate 
        Command classes on your own, but use the Command .execute() method instead.
        """

        # support textual cli arguments
        if cli_args is not None:
            parser = self._configure()
            kargs.update( vars( parser.parse_args( cli_args.split() ) ) )
        
        self.args = kargs
        for name, arg in self.__class__.getargs():
            setattr( self, name, kargs[ arg.name ] )

    # 
    @classmethod
    def getargs( cls ):
        """ Returns the sorted list of Arguments that were defined by this class """
        members = inspect.getmembers( cls )
        args = filter( lambda member: isinstance( member[ 1 ], Argument ), members )
        args.sort( key = lambda arg: arg[ 1 ]._creation_order )
        return args

    # converts this class definition to an argparse ArgumentParser instance, including its entire subparsers tree
    @classmethod
    def _configure( cls, parser = None ):
        
        # create the parser
        if parser is None:
            desc = getattr( cls, "command_description", cls.__doc__ )
            parser = CommandParser( description = desc, data = { "command": cls } )

        # add the command arguments to this parser
        for name, arg in cls.getargs():
            args, kargs = arg.params
            parser.add_argument( *args, **kargs )

        # create the subparsers that were defined in the Command's subcommands property
        subcommands = getattr( cls, "subcommands", [] )
        sub = None
        for Subcommand in subcommands:
            if sub is None:
                sub = parser.add_subparsers( parser_class = CommandParser )

            # create the subparser
            name = getattr( Subcommand, "command_name", Subcommand.__name__.lower() )
            desc = getattr( Subcommand, "command_description", Subcommand.__doc__ ) or ""
            desc = desc.strip()

            subparser = sub.add_parser( name, help = desc, description = desc, data = { "command": Subcommand } )
            Subcommand._configure( subparser )

        return parser

    # 
    @classmethod
    def execute( cls, *args ):
        """ Process the command-line arguments and run the relevant Command """
        parser = cls._configure()
        parsed = parser.parse_args( *args )
        Command = parsed.data[ "command" ]
        Command( **vars( parsed ) ).run()

##
class Argument( object ):
    """ 
    The Argument class provides a low-level of abstraction on top of argparse's add_argument method.
    It's basically an interface for including command-line arguments in the Command classes in 
    an OOP native way
    """

    # trick for maintaining the order in which the Arguments were created in every classes.
    # inspired by Django's implementation of the same requirement
    _creation_order = 0

    # this constructor doesn't really do much except for storing the input for argparse's 
    # add_argument method which is later used by the Command classes in order to generate the parsers tree
    def __init__( self, *args, **kwargs ):
        """
        Creates a new command-line argument. See argparse add_argument() documentation
        """

        Argument._creation_order += 1
        self._creation_order = Argument._creation_order

        self.name = args[ 0 ].replace( "-", "" )
        self.params = ( args, kwargs )


##
class CommandParser( argparse.ArgumentParser ):
    """ 
    This class is a simple wrapped around argparse's ArgumentParser that provides a facility for 
    storing arbitrary data for this parser, and add this data to the parsed arguments

    Usage: 
        parser = CommandParser( data = 5 )
        args = parser.parse_args([])
        print args.data # print 5

    Note that unlike most of argparse's behavior, here the data argument will allow subparsers to override
    their parent's data arguments.

    """

    _data = None 

    # store the arbitrary data for this parser
    def __init__( self, *args, **kargs ):
        if "data" in kargs:
            self._data = kargs[ "data" ]
            del kargs[ "data" ]

        super( CommandParser, self ).__init__( *args, **kargs )

    # attached the previously stored data to the returned namespace
    def parse_known_args( self, *args, **kargs ):
        namespace, arg_strings = super( CommandParser, self ).parse_known_args( *args, **kargs )

        # assign the data only if it wasn't already assigned by a different Command
        if not hasattr( namespace, "data" ):
            setattr( namespace, "data", self._data )

        return namespace, arg_strings

## convinient boolean conversion type that accepts boolean-like strings (yes, true, on)
def bool( value ):
    value = str( value ).lower().strip()
    return value in [ "true", "yes", "on", "1" ]