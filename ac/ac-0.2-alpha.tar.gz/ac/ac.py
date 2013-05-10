import os
import subprocess
import string
from argparse import ArgumentParser
from collections import OrderedDict
import sys

# Command Line Arguments
parser = ArgumentParser("Configure Mogu to create a Makefile")

parser.add_argument("-v","--verbose", dest="verbose", default=False, 
        help="Turn on verbose output", action="store_true")

parser.add_argument("-c", "--compiler", dest="compiler", default="g++",
        help="Default C/C++ Compiler to use", action="store")

parser.add_argument("--nocolor",dest="nocolor",default=False,
        action="store_true", 
        help="Turn this on to disable output coloring. "
        "This is useful if your output looks garbled, or you find colors "
        "more annoying than helpful.")

parser.add_argument("--width", default=80,type=int,dest="width",action="store",
        help="Control the width of the output.")

parser.add_argument("--shell", default="bash",type=str,
        dest="shell",action="store", 
        help="The shell to use when executing fail alternative scripts.")

parser.add_argument("--yes", default=False, action="store_true",
        help="Automatically answer yes to all questions.")

parsed_args= parser.parse_args()

TEST_RESULTS = OrderedDict()
ALL = 0
VERBOSE = parsed_args.verbose
STDOUT = None
STDERR = None
DISTRO = None
shell_output = []
FAIL_ALTERNATIVES = {}


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

COLORS = colors()
if parsed_args.nocolor:
    COLORS.disable()

def if_fail(testname, platform, instruction=None):
    """
        You can define bash script instructions for what to do
        if a test fails, depending on the user's platform. 
        The platform is determined by 'uname -v'. Because platforms
        are not always consistent with how they are labeled, we only 
        store all lower case letters to test against.

        You can pass things in atomically, like:
            if_fail('foo', 'ubuntu', 'sudo apt-get install bar')
        or:
            if_fail('foo',('debian','ubuntu'), 'sudo apt-get install bar')
        or:
            if_fail('foo',{
                   "debian" :   "sudo apt-get install bar",
                   "ubuntu" :   "sudo apt-get install bar1.4-dev",
                   "redhat" :   "sudo yum install bar"
            })
        Regardless of your input, it will all be stored the same:

        {
            "testname"  :   {
                                "platform0" : "instruction0"
                                "platform_n": "instruction_n"
            }
        }


        The instructions will not be executed on the command line, but instead
        written into a bash script which will be executed. This allows you to
        write multiline scripts if you wish, or store scripts externally so
        they can be run apart from this test suite.

        with open("install_foo", "r" as alternative):
            ac_fail("testname","debian",alternative.read())

        Alternatively, you may use ALL as the platform argument to attempt
        the alternative no matter what platform the user has.
    """
    global ALL
    if testname not in FAIL_ALTERNATIVES:
        FAIL_ALTERNATIVES[testname] = {}

    if isinstance(platform, str) or (platform is ALL):
        FAIL_ALTERNATIVES[testname] = {platform : instruction}

    elif isinstance(platform,(tuple,list)):
        for plat in platform:
            FAIL_ALTERNATIVES[testname] = \
                    {plat : instruction}

    elif isinstance(platform,dict):
        FAIL_ALTERNATIVES[testname] = platform

    else:
         raise TypeError("Please provide a valid object for platforms")

# FILTERS

def remove_empty(entry):
    """
        Filters all empty strings and 'None' entries from a list
    """
    return entry != None and entry != ""

def nonalpha_filter(element):
    """
        Removes non-alpha characters from a filtered string.
    """
    return element in string.ascii_letters

def alphaonly(string):
    """
        Given a string, filters out all non-alpha characters
    """
    string = list(string)
    string = filter(nonalpha_filter,string)
    string = "".join(string)
    return string


# UTILITY FUNCTIONS #

def coerce_list(obj):
    """
        Always returns a list.
    """
    if isinstance(obj,list):
        return obj
    elif isinstance(obj,tuple):
        return list(obj)
    elif isinstance(obj,(int,str)):
        return [obj]



def combine_output():
    """
        Given STDERR and STDOUT output, (global), combines them both into one
        list of outputs.This operates globally, and will overwrite the last
        stateful information retrieved.
    """
    global shell_output # R/W
    global STDOUT       # R/W
    global STDERR       # R/W
    global VERBOSE      # R
    STDOUT = coerce_list(STDOUT)
    STDERR = coerce_list(STDERR)
    shell_output=  []
    if STDOUT:
        shell_output.extend(STDOUT)
    if STDERR:
        shell_output.extend(STDERR)

    shell_output = [s.replace("\n","") for s in shell_output if s]

    if VERBOSE:
        sys.stdout.write("OUTPUT: %s" % (str(shell_output)+"\n"))
    

def format_output(*args):
    """
        Attempts to ensure uniform formatting for test results ouptut.
    """
    global parsed_args

    left    = " ".join(args[:-1])
    end     = args[-1]
    width   = parsed_args.width
    spacer  = width - (len(left) + len(end))
    
    if spacer < 1:
        spacer = 1
        left = left[:width-len(end)-1]
    output = left + (" "*spacer) + end
    return left + (" "*spacer) + end

    
def get_shell_output(command,*args):
    """
        Returns a list of all output from the last run command,
        where every line of output separated by a newline character is
        its own element in the list.
    """
    global shell_output
    global STDOUT
    global STDERR

    if not isinstance(command,list):
        command = [command]
    if (args):
        command.extend(args)
    proc = subprocess.Popen(command, shell=False, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    STDOUT,STDERR = proc.communicate()

    if STDOUT:
        if VERBOSE:
            sys.stdout.write("STDOUT: %s\n" % STDOUT)
        filter(remove_empty,STDOUT)

    if STDERR:
        if VERBOSE:
            sys.stderr.write("STDERR: %s\n" % STDERR)
        filter(remove_empty,STDERR)

    combine_output()
    
    return shell_output

def testexe(exename,required=False):
    """
        You can use this to see whether a global executable exists on a system.
        This works by using the 'which' command, and stores the absolute
        path for the command in the TEST_RESULTS (or False if none)
    """
    global TEST_RESULTS
    output = get_shell_output("which", exename)
    if not output:
        test(exename,False,required)
    else:
        test(exename,True,required)
        TEST_RESULTS[exename] = output[0]


def compilecmd(inputfile):
    """
        Creates a GCC compiler command given an input file. The output will
        be named the same as input, without any extension. 
            foo.cpp -> foo

        The exact command will be already formatted for use in
        subprocess.Popen as a list, and can be extended by using the extend
        method: 
            cmd = compilecommand("foo.cpp")
            cmd.extend("-lsomelib")
     """

    global parsed_args
    global VERBOSE
    cmd = [
            parsed_args.compiler,
            "-o", inputfile.split(".")[0],
            inputfile
            ]
    assert cmd != None
    return cmd

def mockc(header=None,func=None,args=None):
    """
        Creates a mock c/c++ script. By default, the script
        will simply run:
            int main() { return 0; }
        However, if you provide a header, function, and list of arguments,
        it can do slightly more:
        mockc(header="myinclude.h", func="foobar",args=["baz","bip",42])
        will generate:
            #include <myinclude.h>
            int main() {
                foobar("baz","bip",42);
            }
    """
    output = "int main() {\n"
    if header: 
        output = ("#include <%s>\n" % header) + output
    if func:
        output += "%s(%s);\n" % (func,
                ",".join(args) if args else '')
    output += "return 0;\n}\n"
    if VERBOSE:
        sys.stdout.write(output)
    return output

def test(testname, result, pass_required=False):
    """
        Tests any arbitrary argument. The testname
        can be anything, and the result must equate
        to either True or False. The result will be
        stored in TEST_RESULTS. 

        If pass_required is set to True, and test is 
        a failure, the configure script will stop unless
        there is a FAIL_ALTERNATIVE provided for the test
        name for the user's Linux distribution.

        If the user has enabled the --yes flag, any alternatives
        will automatically be attempted.
    """
    global COLORS
    def colorize(color,text):
        return color + text + COLORS.ENDC
    global TEST_RESULTS
    TEST_RESULTS[testname] = result
    write = sys.stdout
    color = COLORS.OKGREEN
    if not result:
        color = COLORS.FAIL
        write = sys.stderr
    write.write(
            format_output(
                colorize(color, "%s OK?" % testname),
                colorize(color, " %s\n" % result)))
    if not result and pass_required:
        write.write(
                colorize(COLORS.WARNING,
                "Success is required before "
                "configuration can continue. Aborting.\n"))
        sys.exit()

def require(testname, result):
    """
        A short hand for test(testname, result, True),which makes it
        easier to read the configure script:
            test("foo", True, True) 
            require("foo", True)
        are equivalent.
    """
    test(testname,result,True)

def testheader(header,args=None, required=False):
    """
        Creates a standalone mock c/c++ script
        which tests for a header's existence.
    """
    filename = "configtest_%s" % alphaonly(header)
    cppfile = "%s.cpp" % filename
    with open(cppfile, "w") as f:
        f.write(mockc(header=header,args=coerce_list(args)))
    cmd = compilecmd(cppfile)
    if VERBOSE:
        sys.stdout.write("Header Test: %s\n"% (" ".join(cmd)))
    result = get_shell_output(cmd)
    test(
            header,
            not result,
            required)

def requireheader(header,args=None):
    """
        Shorthand for testheader(header,args,True)
    """
    testheader(header,args,True)

def testlib(libname, func=None, header=None, args=None, required=False):
    """
        Tests for the existence of a library. By default, only
        attempts to link to the library, but you may provide
        a header, function, and function arguments if you wish to
        test something more specific within the library.
    """
    global VERBOSE
    
    filename = "configtest_%s" % libname
    cppfile = "%s.cpp" % filename
    
    with open(cppfile,"w") as f:
        f.write(mockc(header,func,args))

    cmd = compilecmd(cppfile)
    cmd.append("-l%s" % libname)

    if VERBOSE:
        out = "%s\n" % " ".join(cmd)
        sys.stdout.write(out)

    result = get_shell_output(cmd)
    test(
            libname, 
            not result,
            required)

def requirelib(libname,func=None,header=None,args=None):
    """
        Shorthand for testlib() with the required flag set to True.
    """
    testlib(libname,func,header,args,True)

def clean():
    """
        Removes all generated test scripts and files.
    """
    os.system("rm -f configtest_*")


get_shell_output("uname", "-v")
DISTRO = shell_output[0].lower()

