
"""\
Fourlth Loader
--------------

The loader accepts input and does one of several things with it.

First, it breaks the input up into "words" delimited by whitespace.
It then looks at each word to see if it is 

* the start of a string literal (.")
* the start of a comment
* a loader-level command (GO, CLEAR, or LOAD)
* none of the above

In the last case it simply passes the word to the interpreter instance being "compiled".
This word could be a reserved word, a defined word, or a literal.  In any case, it will
be processed and appropriately assimilated into the "proggy" being compiled in the instances
"outer" intepreter.

String Literals
...............

String literals start with a dot-quotation (.") word and include all subsequent words
up to and including one that ends with a quotation character.   ANYTHING that followes
the string literal start character will be included in the literal until this end-of-string-literal
indication is encountered.  This includes comments as well as any reserved words, defined words, 
or other literals.

Comments
........

Comments come in two forms.  The simplest form is a backslash, which tells
the loader to ignore the rest of the line.  This works much the same way as the 
hash mark in shells or python, or the double-slash (//) in C++ or ANSI-C.

The longer form of comments begin and end with parentheses.  Comments must start
with an open paren BY ITSELF -- not prepended to any other non-blank characters -- 
and end with a closing paren, which may or may not be appeneded to one or more non-blank
characters.

Loader Commands
...............

Several words are actually loader-level commands, which are acted upon by the loader
itself rather than being passed along to the interpreter instance for compilation 
and/or execution.

GO (run proggy contained in this interpreter instance)
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Once a program has been loaded into an interpreter instance, one would, presumably,
like to execute it.  This is what the *GO* command is for.   It may appear anywhere in
the input stream -- it is treated more or less as any other word -- but will cause
everhtning up to that point to be executed.   Furthermore, anything that follows
will be ignored.

CLEAR (delete the current instance and create a new one)
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

This instantiates a new interpreter completely replacing the old one.  Any and
all defined words are scattered into oblivion along with the old instance.

LOAD ( filename -- ) 
,,,,,,,,,,,,,,,

Loads *filename* into the corrent interpreter instance.  *filename* is entered as a string literal.
For example:

..code-block:
 
     ." fourlth/test.py" LOAD

"""

import sys
import os

from __init__ import *


def loader(infile, prompt_str=None, interp=None):

    string_acc = None         # Used for accruing
    last_str = None           # string literals.

    in_comment = False        # state flag to indicate whether we're simply
    old_prompt = None         # iterating through words within a long-form comment.

    # Create an interpreter and compile the input
    if interp is None: interp = FourlthInterpreter()

    while True:
        if os.isatty(infile.fileno()):
            try:
                source = raw_input(prompt_str)
            except EOFError:
                sys.exit(1)

            except KeyboardInterrupt:
                print '<< Interrupt! >>'
                continue

        else:
            source = infile.readline()
            if source in ('', None):  # EoF
                return interp

        tups = source.strip().split()

        for w in tups:

            # We handle string literals here, at this level
            if string_acc is None and w in ('."', 'ABORT"'):  # Start processing a string literal
                string_acc = list()

            elif string_acc is not None:
                if w[-1] == '"':  # end processing string literal
                    string_acc.append(w[:-1])
                    last_str = " ".join(string_acc)
                    interp = interp[last_str]
                    string_acc = None

                else:
                    string_acc.append(w)

                continue

            # Loader command (or an in-line (short-form) comment.)
            # Break out of this (inner) loop now and process this.
            if w in ('GO', 'CLEAR', '\\', 'LOAD'):
                if not in_comment:
                    break

            # Comments ...
            if w == '(':
                in_comment = True
                if prompt_str is not None: 
                    old_prompt = prompt_str
                    prompt_str = 'cmt> '
                continue

            elif in_comment and (w[-1] == ')'):
                in_comment = False
                if old_prompt is not None:
                    prompt_str = old_prompt
                    old_prompt = None
                continue

            # Everything else gets "compiled" ...
            if not in_comment:
                interp = interp[w]

        # Load-level commands processed here.
        if w == 'CLEAR':
            interp = FourlthInterpreter()    # Old interp instance is discarded and gc'd.

        elif w == 'LOAD':                    # Load this instance with content from file named
            interp = loader(open(last_str, 'r'), prompt_str=None, interp=interp)
            last_str = None

        # Run the program compiled in this instance thus far.  (In essence,
        # invoke the inner interpreter.)
        elif w == 'GO': 
            if os.isatty(infile.fileno()):   # Run it, if possible
                try:
                    print interp() or '',

                except FourlthSyntaxError:
                    exc = sys.exc_info()
                    print 'SYNTAX ERROR: {0}'.format(exc[1])
                    stackTrace(exc[2])
                    
                except (FourlthRuntimeError, IndexError, IOError):
                    exc = sys.exc_info()
                    print 'RUNTIME ERROR: {0}'.format(exc[1])
                    stackTrace(exc[2])
                    
                except FourlthAbort:
                    exc = sys.exc_info()
                    print 'ABORT: {0}'.format(exc[1])
                    #stackTrace(exc[2])
                    
                except EOFError:
                    break
                
                except KeyboardInterrupt:
                    print '<< Interrupt! >>'

            else:
                return interp

        if os.isatty(infile.fileno()): 
            print 'OK'


