"""\
FoURLth
=======

*FoURLth* stands for *URLs in forth*.  Forth is an early, third-generation programming language 
created by Charles Moore in the early 1970s on an IBM 1130.  He thought of it as more of a fourth-generation
language and would have named it "fourth" but for the ract that file names on the 1130 could only be
five characters long at the time.   Hence, *forth*.

Forth makes heavy and more or less explicit use of a stack to maintain execution state.   Because of its
stack-orientedness, *RPN* (Reverse Polish Notation) works naturally for writing forth programs. 

This module works in a python *pyramid* environment using traversal to decode a URL into a forth program.
Whereas an actual forth program that multiplies two numbers and then squares them might look like this:

..code-block: forth

 12 27 * dup *

The equivalent foURLth "program" would look just like a URL: ``http://fourlth.com/12/27/*/dup/*``

Interaction with Pyramid
------------------------

The *FourlthInterpreter* class is designed to work like a pyramid traversal *resource*, so it
has a ``__getitem__`` method, as well as other methods that can be invoked once the "program" has
been decoded and is ready to run.  

The default view simply returns a JSON object that contains the word ``result`` associated with
whatever the top of the stack was at the end of execution.  If the stack is empty, this value will be ``null``.
There are two other view callables included for demonstration and debugging purposes.

The pyramid traversal algorithim will scan the ``PATH_INFO`` portion of this URL, calling the
resource's ``__getitem__`` method to look up each element.  However, rather than returning the result of
a lookup, the element is incorporated into the "program" being pseudo-compiled and the resource itself
gets returned again.    

Where new words are being defined, the returned resource is actually a new *FourlthInterpreter* instance
that will be embedded in the current one.   More or less the same scheme is used for IF-ELSE-THEN and
LOOP constructions.

Why Bother?
-----------

The idea was to come up with a way to create highly-customized, server-side functions, safely, that could
be rapidly engineered and deployed in web applications.  Specifically, I wanted to have a simple query
engine that could access gene expression data (microarray or RNA seq) and metadata that are part of a larger,
web-based application.   The idea was to be able to, for example, do a search for genes by symbol, then find out
which, if any, datasets had expression information for those genes.   Such a query might look like:

..code-block:

 http://fourlth.net/Gata5/Myb/genesearch/ANY/datasetsearch/metadata

which mightthen return

..code-block:

 { 'genes': ['Gata5', 'Muyb'], 'datasets': ['hiltonlab' { 'celltypes:' [...] }, ...] }

This JSON object could then be used by client-side logic to populate the web, dynamically.

An addition to building in querying capability, I've also built in several analytical tools.
One could, theoretically, also incorporate an *R* interpreter via the *rpy2* module, but
that necessarily bloats the size of the server-side portion of the application.  Care should be taken 
when doing this.


Nick Seidenman <seidenman@wehi.edu.au>
Molecular Medicine
Walter and Eliza Hall Institute
Parkville, VIC
Australia

"""

import logging
log = logging.getLogger(__name__)


import math
import sys

from types import FunctionType, LambdaType, MethodType

from core import *

from exc import *

class FourlthInterpreter(object):

    def __init__(self, request=None, parent=None, branch=None):
        self._parent = parent
        self.dictionary = base_dictionary if parent is None else parent.dictionary
        if not self.dictionary.has_key('VARIABLES'): self.dictionary['VARIABLES'] = { }
        self._stack = list() if parent is None else parent._stack
        self._I = None
        self._proggy = list()
        self._request = request
        self._name = branch



    def __getitem__(self, word):
        """\
"Compile" *word* by seeing if it is already defined or is itself the begining 
of a new word definition.   If it is already defined (i.e. is found in this instance's
dictionary), add the correspond *FunctionType* objection to this instances "program"
body.  Then, return this instance to the caller.

If is a new word defintion, create a new interpreter instance and pass this back to 
the caller without any further action.  Loops and IF-ELSE-THEN blocks are handled similarly.

In threaded interpretive language parlance, this would be considered the "outer" interpreter.
"""
        # Definining new words is a bit of a special case.
        # . . . 
        # Start a new word definition.   
        # Create a new (parented) instance of the interpreter.
        # We then switch context (for the purpse of building the overall
        # fourlth proggy) to this new intepreter.
        if word == ':':  # We're defining a new word.
            return FourlthInterpreter(self._request, parent=self)

        # When we start out, the first word after the colon (:) is the
        # mnemonic for the new word.  So we stash this away for later
        # and do NOTHING else.
        if self._parent is not None and self._name is None:
            log.debug("definining new word '{0}'".format(word))
            self._name = word
            return self

        # End of the new definition.   Associated this interpreter
        # instance with the mnemonic we saved from before.
        # Return the parent as the current context.
        if word == ';':
            log.debug("end definition of '{0}'".format(self._name))
            self._parent.dictionary[self._name] = self
            return self._parent

        # IF...ELSE...THEN 
        if word == 'IF':
            return FourlthInterpreter(self._request, parent=self, branch='IF...block')
        
        if word == 'ELSE':
            if self._parent is None or self._name != 'IF...block':
                log.error('ELSE without corresponding IF')
                raise FourlthSyntaxError('ELSE without corresponding IF')
            
            self._alt_proggy = self._proggy
            self._proggy = list()
            return self

        if word == 'THEN':
            if self._parent is None or self._name != 'IF...block':
                log.error('ELSE without corresponding IF')
                raise FourlthSyntaxError('ELSE without corresponding IF')

            if hasattr(self, '_alt_proggy'):
                temp = self._proggy
                self._proggy = self._alt_proggy
                self._alt_proggy = temp
            else:
                self._alt_proggy = list()

            self._parent._proggy.append(self)
            return self._parent

        # ABORT"... "
        if word == 'ABORT"':
            return FourlthInterpreter(self._request, parent=self, branch="ABORT")
        
        if word == '."':
            return FourlthInterpreter(self._request, parent=self, branch="STRING")

        # Definite loops (DO...LOOP)
        if word == 'DO':
            return FourlthInterpreter(self._request, parent=self, branch='DO...LOOP')
            
        if word in  ('LOOP', '+LOOP'):
            if self._parent is None or self._name != 'DO...LOOP':
                log.error('LOOP without corresponding DO')
                raise FourlthSyntaxError('LOOP without corresponding DO')

            if word == '+LOOP':
                self._proggy.append(lambda x: x.incr(x.pop()))
            else:
                self._proggy.append(lambda x: x.incr())

            self._parent._proggy.append(self)
            return self._parent

        # Indefinite loops (BEGIN...UNTIL (and BEGIN...WHILE...REPEAT)
        if word == 'BEGIN':
            return FourlthInterpreter(self._request, parent=self, branch='BEGIN...')

        if word == 'UNTIL':
            if self._parent is None or self._name != 'BEGIN...':
                log.error('UNTIL without corresponding BEGIN')
                raise FourlthSyntaxError('UNTIL without corresponding BEGIN')

            self._name = self._name + 'UNTIL'
            self._parent._proggy.append(self)
            return self._parent

        if word == 'WHILE':
            if self._parent is None or self._name != 'BEGIN...':
                log.error('WHILE without corresponding BEGIN')
                raise FourlthSyntaxError('WHILE without corresponding BEGIN')

            self._name = self._name + 'WHILE...'
            self._proggy.append(lambda x: x._while())
            return self

        if word == 'REPEAT':
            if self._parent is None or self._name != 'BEGIN...WHILE...':
                log.error('REPEAT without corresponding BEGIN...WHILE')
                raise FourlthSyntaxError('REPEAT without corresponding BEGIN...WHILE')

            self._name = self._name + 'REPEAT'
            self._parent._proggy.append(self)
            return self._parent

        # Immediate loop exit.
        if word == 'LEAVE':
            self._proggy.append(self._leave)
            
            
        # Normal proggy-building stuff.  If the word has a definition then
        # push the corresponding object (function/interpreter) instance onto
        # the "compiled" proggy list.  Otherwise, assume it's a constant of 
        # some kind and just wrap it in an anonymous function that'll simply
        # return it when called.
        if word in self.dictionary:
            word = self.dictionary[word]

        else:
            # See if we have an integer constant.  If so, decode it as such.
            # Otherwise, just push the string value on the stack
            try:
                term = int(word)
            except:
                term = word
            word = lambda x: term

        self._proggy.append(word)
        
        if self._name in ('STRING', 'ABORT'):
            self._parent._proggy.append(self)
            return self._parent

        return self


    def __len__(self): 
        """Returns current depth of the stack."""
        return len(self._stack)


    def _exec(self, program):
        """\
Execute each word in the sequence of callables contained in *program*.
If the result of execution is not ``None``, push whatever it is onto the stack.
"""
        for step in program:
            result = step(self)
            if result is not None:
                self.push(result)
        return

    def _leave(self, dummy=None):
        """\
This implements the ``LEAVE`` word by raising the ``FourlthBreak`` exception,
which can then be trapped.
"""
        log.debug('Leaving {0}'.format(self._name))
        raise FourlthBreak(self._name)

                              
    def _while(self):
        """\
Similar to ``_leave``.  This will raise ``FourlthBreak`` exception
when conditions are met for exiting a ``WHILE`` or ``UNITL`` loop.
"""
        if self.pop() == 0:  
            log.debug('WHILE / UNTIL loop exit condition met'.format(self._name))
            raise FourlthBreak(self._name)

        return None

    def __call__(self, *args, **kwargs):
        """\
Whereas ``__getitem__ is the outer intepreter, this is the *inner* interpreter.
Here we iterate through the interpreter instance's program body (proggy) executing
each "word" as we go.  Some words are in fact other interpreter instances.  Either way,
the same semantics can be used.  (Thank you, Guido!!) 

XXX I'm considering breaking this all up into subclassed interpreters. 

   FourlthIntepreter  # base class
       |
       +--- FourlthIfElseThenBlock
       |
       +--- FourlthDOLoop
         :

Each would then have an instance added to the parent instance's *proggy* (root parent would
be an instance of the base class, I think.)   (sigh -- spending waaaay too much time on this, but
a fun learning exercise, no?  nls)

"""
        log.debug('executing ' + (self._name or 'root'))
        if self._parent is not None: self._stack = self._parent._stack

        program = self._proggy
        start = 0
        finish = 1

        # Process IF-ELSE-THEN constructs here...
        if self._name == 'IF...block':
            if self.pop() == 0: program = self._alt_proggy
            self._exec(program)

        # ABORT" works sorta like an IF..THEN (no ELSE)
        elif self._name == 'ABORT':
            self._exec(program)
            msg = self.pop()
            if self.pop() != 0:
                raise FourlthAbort(msg)

        # Process definite loops here...
        elif self._name == 'DO...LOOP':
            self._I = self.pop()
            finish = self.pop()

            while self._I < finish:
                try:
                    self._exec(program)
                except FourlthBreak(self._name):
                    break

        # We handle both types of indefinite loop here.  A "false"
        # condition result for the WHILE clause will result in
        # FourlthBreak being raised.
        elif self._name is not None and self._name[:6] == 'BEGIN.':
            while True:
                try:
                    self._exec(program)
                    if self._name[8:] == 'UNTIL' and self.pop() != 0:
                        break;
                except FourlthBreak(self._name):
                    break

        # Everything else comes here.
        else:
            self._exec(program)
        
            
        log.debug('stack: {0}'.format(self._stack))
        return self.pop() if len(self._stack) > 0 else None


    # -- STACK MANIPULATION -- #
    # (Note, all of these are exposed in core.py and probably should be called
    # through those functions, rather than directly.   Don't ask me why.  Just
    # ... do it, ok?  nls
    def push(self, word):
        log.debug('pushing {0} <- {1}'.format(self._stack, word))
        self._stack.append(word)

    def pop(self):
        if len(self._stack) < 1:
            raise IndexError('stack is empty!')

        word = self._stack.pop()
        #if isinstance(word, (FunctionType,LambdaType, MethodType)): word = word(self)
        log.debug('popping {0} -> {1}'.format(self._stack, word))
        return word

    def swap(self):
        x, y = self.pop(), self.pop()
        self.push(x)
        self.push(y)
        return None

    def rot(self):
        top3 = [ self.pop() for i in range(3) ]
        self.push(top3[1])
        self.push(top3[0])
        self.push(top3[2])
        return None

    def over(self):
        self.push(self._stack[-2])
        return None

    def tuck(self):
        self._stack.insert(-2, self._stack[-1])
        return None

    def pick(self):
        self.push(self._stack[-(self.pop()+1)])

    def roll(self):
        self.push(self._stack.pop(-(self.pop()+1)))
        
    # -- (end) STACK MANIPULATION ... NOW!! -- #

    # "I" is the current loop index.  "J" is the index of the nearest
    # outer loop relative to "I".
    @property
    def index(self):
        return (self._I, self.parent._I if self._parent is not None else None)
    
    def incr(self, val=1):
        log.debug('incrementing loop: {0} -> {1}'.format(self._I, self._I+val))
        self._I += val
        return None

    @property
    def name(self): 
        return self._name

    @property
    def parent(self):
        return self._parent
    

        
