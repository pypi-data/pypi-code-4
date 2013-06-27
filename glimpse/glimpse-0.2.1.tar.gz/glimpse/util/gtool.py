"""Operate on data files."""

# Copyright (c) 2011-2013 Mick Thomure
# All rights reserved.
#
# Please see the file LICENSE.txt in this distribution for usage terms.

import importlib
from numpy import *
import numpy as np
import os
import sys

from glimpse.util.option import *

class CircularDependency(Exception):
  pass

class NamespaceWrapper(dict):
  """A wrapper for the locals() dictionary.

  The logic that is added includes:
    - rewrite variable name "o" to "result"
    - process variable names "lines", "table", and "num_table" as calls to
    lines(), table(), and num_table(), respectively.
    - rewrite "result" (or "o") as an RVALUE to "table" when the
      variable is empty.
    - process variable name "num_words" as call to map(float, words)
  """

  #: Variables that will be rewritten as other variables.
  var_rules = {}

  #: Variables that will be rewritten as calls to functions.
  func_rules = {}

  def __init__(self, vs, var_rules = None, func_rules = None):
    #: Set of local variables.
    self.vs = vs
    if var_rules:
      self.var_rules = var_rules
    if func_rules:
      self.func_rules = func_rules

  def _lookup(self, item):
    """Dealias a symbol name."""
    stack = set()
    while item in self.var_rules:
      if item in stack:
        raise CircularDependency
      stack.add(item)
      item = self.var_rules[item]
    return item

  def get(self, item, default = None):
    """Lookup an item from the dictionary.

    Apply variable rewrites before function rewrites.

    """
    try:
      return self[item]
    except KeyError:
      return default

  def __getitem__(self, item):
    item = self._lookup(item)
    if item in self.func_rules:
      # Replace an RVALUE symbol with the results of a function call.
      func = self.func_rules[item]
      result = func()
    else:
      # Try to resolve the symbol in the local namespace. If this fails, it will
      # cause the evaluator to look for the symbol in the global namespace
      # instead.
      result = self.vs[item]
    return result

  def __contains__(self, item):
    item = self._lookup(item)
    return (item in self.vs)

  def __setitem__(self, item, value):
    item = self._lookup(item)
    self.vs[item] = value

  def VarRule(self, **kwargs):
    """Add a rule to alias two variable names."""
    for k, v in kwargs.items():
      if not isinstance(v, basestring):
        raise ValueError("Rewrite value must be a string, but got: %s" % (v,))
      self.var_rules[k] = v

  def FuncRule(self, **kwargs):
    """Add a rule to alias a variable name with a function call."""
    for k, v in kwargs.items():
      if not hasattr(v, '__call__'):
        raise ValueError("Rewrite value must be a function, but got: %s" % (v,))
      self.func_rules[k] = v

class HelpfulNamespaceWrapper(NamespaceWrapper):

  def GetSymbols(self):
    symbols = dict()
    for k, v in self.var_rules.items():
      symbols[k] = "alias for %s" % v
    for k, v in self.func_rules.items():
      symbols[k] = v.__doc__
    return symbols

class FileNamespace(HelpfulNamespaceWrapper):

  # Caches for whole-input function calls.
  _lines = None
  _table = None
  _num_table = None

  def __init__(self, vs, fh = sys.stdin, word_delimiter = " ", numeric = False):
    super(FileNamespace, self).__init__(vs,
        var_rules = dict(o = "output", result = "output", t = "table"),
        func_rules = dict(table = self.table, lines = self.lines,
            num_table = self.num_table,
            ))
    self.fh = fh
    self.word_delimiter = word_delimiter
    if numeric:
      self.VarRule(table = "num_table")

  def lines(self):
    """input as a list of lines"""
    if self._lines == None:
      self._lines = list( _.strip() for _ in self.fh.readlines() )
    return self._lines

  def table(self):
    """input as a 2D list of words"""
    if self._table == None:
      self._table = [ _.split(self.word_delimiter) for _ in self.lines() ]
    return self._table

  def num_table(self):
    """input as a 2D array of floats"""
    if self._num_table == None:
      self._num_table = np.array([ map(float, _.split(self.word_delimiter))
          for _ in self.lines() ])
    return self._num_table

  def get_output(self):
    """Get the current output buffer, using the input buffer if undefined."""
    output = self.vs["output"]
    return output

class LineNamespace(HelpfulNamespaceWrapper):

  def __init__(self, vs, numeric = False):
    super(LineNamespace, self).__init__(vs,
        var_rules = dict(o = "output", result = "output", w = "words",
            l = "line", n = "num"),
        func_rules = dict(num_words = self.num_words,
        ))
    if numeric:
      self.VarRule(words = "num_words")

  def num_words(self):
    """current line as a 1D numpy array of floats"""
    return np.array(map(float, self.vs["words"]))

  def get_output(self):
    """Get the current output buffer, using the input buffer if undefined."""
    output = self.vs["output"]
    return output

def read_lines(path):
  if isinstance(path, basestring):
    fh = open(path)
  else:
    fh = path
  result = list( _.strip() for _ in fh.readlines() )
  if fh != path:
    fh.close()
  return result

def read_table(path, delim = " "):
  """read contents of file as a table"""
  return [ _.split(delim) for _ in read_lines(path) ]

def read_num_table(path, delim = " "):
  """read contents of file as a table"""
  return np.array([ map(float, _) for _ in read_table(path, delim) ])

def toline(xs):
  """Format a list as a string with one line."""
  return " ".join(map(str, xs)) if hasattr(xs, '__iter__') else str(xs)

def tolines(xss):
  """Format a 2D list as a string with multiple lines."""
  return "\n".join(map(toline, xss)) if hasattr(xss, '__iter__') else str(xss)

def InitPlotting():
  # If the DISPLAY environment variable is set, then assume the plot can be
  # displayed on screen.
  use_file_output = ('DISPLAY' not in os.environ)
  import matplotlib
  if use_file_output:
    matplotlib.use("cairo")
  elif matplotlib.get_backend() == "":
    matplotlib.use('TkAgg')
  # XXX Make symbols available via globals.
  global mpl, plt, plot
  import matplotlib as mpl, matplotlib.pyplot as plt
  plot = plt.plot

class Processor(object):

  fhin = sys.stdin
  fhout = sys.stdout
  numeric = False
  quiet = False
  raw_output = False
  statement = False
  verbose = False
  word_delimiter = " "

  def Log(self, msg):
    if self.verbose:
      print >>sys.stderr, msg

  def Evaluate(self, cmd, vs, codeobj = None):
    """Evaluate (or execute) a command on the input file."""
    if cmd == None:
      raise ValueError("Command must not be empty")
    if codeobj == None:
      codeobj = cmd
    if self.statement:
      self.Log("Evaluated statement:\n  %s" % cmd)
      try:
        exec codeobj in globals(), vs
      except SyntaxError, e:
        sys.exit("Error: Invalid statement\n"
              "  %s\n %s^" % (cmd, " " * e.offset))
      except Exception, e:
        sys.exit("Error: Invalid statement\n"
              "  %s\n%s: %s" % (cmd, e.__class__.__name__, e))
      if 'result' not in vs:
        self.Log("Warning: result is not set")
      result = vs.get('output', None)
    else:
      self.Log("Evaluated expression:\n  %s" % cmd)
      try:
        result = eval(codeobj, globals(), vs)
      except SyntaxError, e:
        sys.exit("Error: Invalid expression\n"
              "  %s\n %s^" % (cmd, " " * e.offset))
      except Exception, e:
        sys.exit("Error: Invalid expression\n"
              "  %s\n%s: %s" % (cmd, e.__class__.__name__, e))
    return result

  def PrintResult(self, result, as_line = False):
    if self.quiet:
      return
    if self.raw_output:
      print result
    elif not (result is None or result is False):
      if as_line:
        result = toline(result)
      else:
        result = tolines(result)
      self.fhout.write(result)
      if not result.endswith('\n'):
        self.fhout.write('\n')

  def ProcessByLine(self, cmd):
    """Evaluate a command once per line of the input file."""
    line = None
    num = None
    words = None
    if not cmd:
      cmd = "line"
    elif cmd == "help":
      _vars = LineNamespace(locals(), numeric = self.numeric)
      symbols = _vars.GetSymbols()
      symbols.update(
          line = "current input line as a single string",
          num = "current line number",
          words = "current input as a list",
          output = "value to print")
      Help(symbols = symbols)
    codeobj = compile(cmd, 'command', 'single' if self.statement else 'eval')
    for numz, line in enumerate(self.fhin):
      line = line[:-1]
      n = num = numz + 1
      words = [w for w in line.strip().split(' ') if len(w)]
      _vars = LineNamespace(locals(), numeric = self.numeric)
      result = self.Evaluate(cmd, _vars, codeobj = codeobj)
      self.PrintResult(result, as_line = True)

  def ProcessAtOnce(self, cmd):
    """Evaluate a command once for the entire input file."""
    result = None  # define here, in case "exec cmd" forgets to assign
    p = self
    _vars = FileNamespace(locals(), fh = self.fhin,
        word_delimiter = self.word_delimiter, numeric = self.numeric)
    if not cmd:
      cmd = "lines"
    elif cmd == "help":
      symbols = _vars.GetSymbols()
      symbols.update(output = "value to print")
      Help(symbols = symbols)
    result = self.Evaluate(cmd, _vars)
    return
    self.PrintResult(result)

def GTool(opts, cmd):
  p = Processor()
  # Pre-processing
  if opts.modules is not None:
    # Import requested modules
    for m in opts.modules:
      m = m.strip()
      globals()[m] = importlib.import_module(m)
  if opts.plotting:
    InitPlotting()
  p.word_delimiter = opts.word_delimiter
  p.numeric = opts.numeric
  p.quiet = opts.quiet or opts.plotting
  p.raw_output = opts.raw_output
  p.statement = opts.statement
  p.verbose = opts.verbose
  # Process data
  if opts.iterate_lines:
    p.ProcessByLine(cmd)
  else:
    p.ProcessAtOnce(cmd)
  # Post-processing
  if opts.plotting:
    import matplotlib.pyplot as plt
    if self.plot_file:
      plt.savefig(opts.plot_file)
    else:
      plt.show()

def MakeCliOptions():
  return OptionRoot(
      Option('word_delimiter', flag = 'd:', doc = "Set the column delimiter "
          "for input data"),
      Option('iterate_lines', flag = 'e', doc = "Evaluate the command for each "
          "line of input, rather than the entire file"),
      Option('help', flag = ('h', 'help'), doc = "Print this help and exit"),
      Option('help_commands', flag = ('H', 'help-cmds'),
          doc = "Print information about available commands and exit"),
      Option('modules', flag = ('m:', 'module='), multiple = True,
          doc = "Import modules before running commands"),
      Option('numeric', flag = 'n', doc = "Treat all input values as numeric"),
      Option('plot_file', flag = ('P:', 'plot-file='), doc = "Save the results "
          "to a file (if -p, save the plot instead"),
      Option('plotting', flag = 'p', doc = "Use plotting commands (implies "
          "-q)"),
      Option('quiet', flag = 'q', doc = "Do not print result (be quiet)"),
      Option('raw_output', flag = 'r', doc = "Print raw output"),
      Option('statement', flag = 's', doc = "Treat command as a statement"),
      Option('verbose', flag = 'v', doc = "Be verbose"),
      )

def Help(options = None, symbols = None):
  if symbols:
    print >>sys.stderr, "The command can contain any of the following symbols:"
    keys = symbols.keys()
    nonalias_keys = [ k for k in keys if not symbols[k].startswith("alias") ]
    alias_keys = [ k for k in keys if symbols[k].startswith("alias") ]
    keys = sorted(nonalias_keys) + sorted(alias_keys)
    fmt = "%%%ds -- %%s" % (max(map(len, keys)) + 2)
    for k in keys:
      print >>sys.stderr, fmt % (k, symbols[k])
  else:
    print >>sys.stderr, "usage: [options] CMD"
    PrintUsage(options, stream = sys.stderr, max_flag_length = 15, width = 80)
  sys.exit(-1)

def Main(argv = None):
  options = MakeCliOptions()
  try:
    args = ParseCommandLine(options, argv = argv)
    if options.help_commands.value:
      cmd = "help"
    elif options.help.value:
      Help(options)
    elif len(args) > 0:
      cmd = args[0]
    else:
      cmd = None
    GTool(OptValue(options), cmd)
  except OptionError, e:
    print >>sys.stderr, "Usage Error (use -h for help): %s." % e
  except KeyboardInterrupt:
    pass

if __name__ == '__main__':
  Main(sys.argv)
