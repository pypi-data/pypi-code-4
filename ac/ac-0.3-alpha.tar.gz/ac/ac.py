import os
import subprocess
import string
from argparse import ArgumentParser
from collections import OrderedDict
from filters import *
import sys
import inspect

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

parser.add_argument("--log", default="stdout", action="store", dest="log",
        help="Where to send verbose output (stdout, stderr, or absolute filename) ")

parsed_args = parser.parse_args()

# Setup for globals
TEST_RESULTS = OrderedDict()
FAIL_ALTERNATIVES = OrderedDict()
ALL = 0 # Used for setting up alternatives regardless of the distro
VERBOSE = parsed_args.verbose

# Because ac is stateful, results of previous tests and commands are 
# preserved here for later use, if desired. 
STDOUT = None
STDERR = None
# This will hold the combined stdout and
# stderr results of the last shell command.
shell_output = []

# This will be set at the end of the import, and based on
# 'uname -v'. The entire output of uname -v will be stored
# as all lowercase. 
DISTRO = None


def log(*args):
    """
        If --verbose or -v is set, this function will
        direct the logged output to stdout by default, stderr
        on request, or a filename if passed in by the user.
        All logs will be prepended by the line number of the
        log request.
    """
    msg = " ".join([str(arg) for arg in args])
    global VERBOSE
    global parsed_args
    if VERBOSE:
        msg = str(msg)
        msg = str(inspect.currentframe().f_back.f_lineno) + ": " + msg
        if parsed_args.log=="stdout":
            sys.stdout.write(msg+"\n")
        elif parsed_args.log=="stderr":
            sys.stderr.write(msg+"\n")
        else:
            with open(parsed_args.log,"a") as f:
                f.write(msg)

class colors:
    """
        Terminal color codes. These may not necessarily work depending, 
        upon the user's terminal environment, but can be disabled from the
        --nocolor switch. 
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        """
            If an instance of this class has been created, turns
            all colors off.
        """
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

COLORS = colors() # Create an instance of colors for toggleable codes
if parsed_args.nocolor:
    COLORS.disable()

def colorize(color,text):
    global COLORS
    return color + text + COLORS.ENDC

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

        Order matters here! You must call the if_fail functionality in the
        order of precedence. For instance, if the 'uname -v' output is:
        'debian-ubuntu', but you want to want to prefer ubuntu over the more
        generic debian alternative, you must pass it in as ("ubuntu","debian").

    """
    global ALL
    if testname not in FAIL_ALTERNATIVES:
        # Create an entry in the FAIL_ALTERNATIVES dictionary
        FAIL_ALTERNATIVES[testname] = {}

    if isinstance(platform, str) or (platform is ALL):
        # Assign the platform's command sequence
        FAIL_ALTERNATIVES[testname][platform] = instruction

    elif isinstance(platform,(tuple,list)):
        # Assign the command sequence to all platforms in the list
        for plat in platform:
            FAIL_ALTERNATIVES[testname][plat] = instruction

    elif isinstance(platform,dict):
        # Copy entries into FAIL_ALTERNATIVES
        FAIL_ALTERNATIVES[testname] = platform.copy()

    else:
         raise TypeError("Please provide a valid object for platforms")

# UTILITY FUNCTIONS #


def coerce_list(obj):
    """
        Always returns a list, no matter what.
    """
    log(type(obj))
    if isinstance(obj,list):
        return obj
    elif isinstance(obj,tuple):
        return list(obj)
    elif isinstance(obj,(int,str)):
        return [obj]
    elif not obj:
        return []



def combine_output():
    """
        Given STDERR and STDOUT output, (global), combines them both into one
        list of outputs.This operates globally, and will overwrite the last
        stateful information retrieved.
    """
    global shell_output # R/W
    global STDOUT       # R/W
    global STDERR       # R/W
    STDOUT = coerce_list(STDOUT)
    STDERR = coerce_list(STDERR)
    if STDOUT:
        shell_output.extend(STDOUT)
    if STDERR:
        shell_output.extend(STDERR)

    shell_output = [s.replace("\n","") for s in shell_output if s]
    log("OUTPUT: %s" % (str(shell_output)))

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

    
def reset_output():
    global shell_output
    global STDOUT
    global STDERR
    log("Resetting output containers")
    shell_output = []
    STDOUT = None
    STDERR = None

def get_shell_output(command,*args):
    """
        Returns a list of all output from the last run command,
        where every line of output separated by a newline character is
        its own element in the list.
    """
    global shell_output
    global STDOUT
    global STDERR

    reset_output()

    if not isinstance(command,list):
        command = [command]
    if (args):
        command.extend(args)
    proc = subprocess.Popen(command, shell=False, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    STDOUT,STDERR = proc.communicate()

    if STDOUT:
        log("STDOUT: %s" % STDOUT)
        filter(remove_empty,STDOUT)
    else:
        STDOUT = None

    if STDERR:
        log("STDERR: %s" % STDERR)
        filter(remove_empty,STDERR)
    else: 
        STDERR = None

    combine_output()
    log("OUTPUT: %s" % shell_output)
    
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

def requireexe(exename):
    testexe(exename,True)

def alternative(testname):
    global DISTRO
    global FAIL_ALTERNATIVES
    global ALL

    if testname not in FAIL_ALTERNATIVES:
        return False
    
    for distro in FAIL_ALTERNATIVES[testname]:
        if distro is ALL:
            return FAIL_ALTERNATIVES[testname][ALL]
        if distro in DISTRO:
            return FAIL_ALTERNATIVES[testname][distro]

    return False

def try_alternative(alt):
    """
        Creates a shell script from the text passed in, and executes it.
        Unless the user has supplied the --yes switch, they will have the 
        opportunity to read and agree to the script first (making --yes
        fairly dangerous, to be honest). 
    """
    global parsed_args
    global STDERR
    global COLORS
    global TEST_RESULTS
    alt = "#!%s\n" % (TEST_RESULTS[parsed_args.shell]) + alt
    if not parsed_args.yes:
        warning = colorize(
            COLORS.WARNING, 
            "\nAlthough the last test failed, the author of this configure\n "
            "script has provided an alternative script for your Linux\n "
            "distribution to be run in order to resolve the missing\n "
            "dependency. \n\n"
            "It is highly recommended that you make sure you understand "
            "the script (displayed below) before continuing, as it may "
            "make changes to the configuration of your computer. AC.py "
            "is not responsible for any side effects of running this "
            "script.\n\n" "You should only continue if you are positive that "
            "the script will not make undesired changes or compromise the "
            "security of your computer.\n\n "
            "====vvvvv SCRIPT TO BE RUN vvvvv====\n\n"
            )
        warning += colorize( COLORS.OKBLUE, alt )
        warning += colorize( COLORS.WARNING,
            "\n====^^^^^^^^^^^^^^^^^^^^^^^^^^^^====\n"
            "To continue, type CONTINUE (all in caps!): "
            "\n\t")
        cont = raw_input(warning)
        if cont != "CONTINUE":
            return False
    alternative_filename = "configtest_alternative.sh"
    with open(alternative_filename, "w") as f:
        f.write(alt)
    os.system("chmod +x %s" % alternative_filename)
    get_shell_output("./%s" % alternative_filename)
    if STDERR:
        log(sys.stdout.write("Errors Executing Alternative: %s\n" % STDERR))
        return False
    log("Alternative Succeeded")
    return True

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
    log(output)
    
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
        will automatically be attempted. Otherwise, a user will
        be shown the script about to run before it is run.
    """
    global COLORS
    global TEST_RESULTS
    

    attempted_alternative = False
    TEST_RESULTS[testname] = result
    write = sys.stdout
    color = COLORS.OKGREEN
    alt_script = None
    if not result:
        alt_script = alternative(testname)
        if alt_script: 
            color = COLORS.WARNING
        else:
            color = COLORS.FAIL
            write = sys.stderr
    write.write(
            format_output(
                colorize(color, "%s OK?" % testname),
                colorize(color, " %s\n" % result)))

    # If the result was a failure, try the alternative.
    if alt_script and not result:
        result = try_alternative(alt_script)
        if result:
            write.write(
                    colorize(COLORS.OKBLUE, 
                    "Alternative Succeeded! %s OK.\n" % testname))
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
    log("Header Test: %s" % (" ".join(cmd)))
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
    
    filename = "configtest_%s" % libname
    cppfile = "%s.cpp" % filename
    
    with open(cppfile,"w") as f:
        f.write(mockc(header,func,args))

    cmd = compilecmd(cppfile)
    cmd.append("-l%s" % libname)
    log("%s" % " ".join(cmd))

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

def set_shell(shellname):
    parsed_args.shell = shellname
    requireexe(shellname)

get_shell_output("uname", "-v")
DISTRO = shell_output[0].lower()

if VERBOSE:
    sys.stdout.write("Distro: %s" % DISTRO)

# Always make sure that the correct shell environment
# is present on the system. 
testexe(parsed_args.shell, required=False)
