
import itertools as it
import operator as op
import subprocess
import traceback
import tempfile
import inspect
import shutil
import copy
import sys
import os


def handled(f):
    def wrapped(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            sys.stderr.write('[Error] Exception in %s:\n' % f.__name__)
            sys.stderr.write(traceback.format_exc(e))
    return wrapped

def justval_parser(line):
    return None, line.strip()

def tab_parser(line):
    return line.strip().split('\t', 1)

def identity_line_breaker(stream):
    return stream

@handled    
def smap(mapper, stream, lp=justval_parser, lb=identity_line_breaker):
    """Stream map: applies mapper to each line in input stream
    reducer function to the whole list of values.
    
     lines          - generator of key-value lines
     mapper(k, v)   - function to be applied to generator of values
     lp             - line parser, i.e. function to extract key and value
                      from input line
     lb             - line breaker, i.e. function to break input stream
                      into 'lines', whatever it means in the context
    """
    lines = lb(stream)
    for line in lines:
        k, v = lp(line)        
        for item in mapper(k, v):
            key, value = item
            print('%s\t%s' % tuple(item))


@handled
def sreduce(reducer, lines, lp=tab_parser):
    """Stream reducer: groups lines by key and applies
    reducer function to the whole list of values.
    
     lines          - generator of key-value lines
     reducer(k, vs) - function to be applied to generator of values
     lp             - line parser, i.e. function to extract key and value
                      from input line
    """
    data = (lp(line) for line in lines)
    for key, group in it.groupby(data, key=op.itemgetter(0)):
        for item in reducer(key, (v for k, v in group)):
            print('%s\t%s' % tuple(item))


def snakeriver_path():
    return sys.modules[__name__].__file__
            
def caller_module():
    frm = inspect.stack()[2]
    mod = inspect.getmodule(frm[0])
    return mod
    # return os.path.abspath(mod.__file__)

    
DEFAULT_JAR = '/usr/lib/hadoop-mapreduce/hadoop-streaming.jar'



def build_app(caller_module, options):
    """Collects all required files and creates application directory in
       temporary location
    """
    files = [snakeriver_path(), os.path.abspath(caller_module.__file__)]
    files += options.get('files', [])
    # create app directory
    tmp_dir = tempfile.mkdtemp()
    app_dir = os.path.join(tmp_dir, 'app')
    os.mkdir(app_dir)
    for fname in files:
        shutil.copy2(fname, app_dir)
    return app_dir

def clean_app(app_dir):
    shutil.rmtree(app_dir)

    
def format_options(app_dir, options):
    formatted = {}
    inputs = options.get('inputs', '.')
    if type(inputs) is not list:
        inputs = [inputs] 
    formatted['inputs'] = '-input ' + ' -input '.join(inputs)
    formatted['output'] = '-output ' + options.get('output', 'out')
    formatted['jar'] = options.get('jar', DEFAULT_JAR)
    formatted['files'] = '-files %s' % app_dir
    return formatted
    
    
def format_command(app_dir, caller_module, options):
    program = os.path.basename(caller_module.__file__)
    opts = format_options(app_dir, options)
    command = 'hadoop jar ' + opts['jar'] + ' ' + opts['files'] + ' '
    command += '-mapper "app/%s map" ' % program
    command += '-reducer "app/%s reduce" ' % program
    if 'combiner' in options:
        command += '-combiner "app/%s combine" ' % program
    command += opts['inputs'] + ' '
    command += opts['output'] + ' '
    return command
    
    
def submitjob(caller_module, options):
    app_dir = build_app(caller_module, options)
    command = format_command(app_dir, caller_module, options)
    exitcode = subprocess.call(command, shell=True, stdout=sys.stdout)
    clean_app(app_dir)
    

def showjob(caller_module, options):
    app_dir = '/tmpXXXXXX/app'
    command = format_command(app_dir, caller_module, options)
    print(command)

    
############ User Functions ###########

def runjob(mapper, reducer, **options):
    """Single interface to run MapReduce jobs
    """
    combiner = options.get('combiner')
    if len(sys.argv) == 1:
        submitjob(caller_module(), options)
    elif sys.argv[1] == 'show':
        showjob(caller_module(), options)
    elif sys.argv[1] == 'map':
        smap(mapper, sys.stdin)
    elif sys.argv[1] == 'reduce':
        sreduce(reducer, sys.stdin)
    elif sys.argv[1] == 'combine':
        if combiner:
            sreduce(combiner, sys.stdin)
        else:
            raise Exception('Combiner is not specified')

    
