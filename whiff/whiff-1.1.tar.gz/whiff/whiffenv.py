"""
String constants used to store information in the WSGI environment to aid communication between components.
"""

import types

#####################
# CLIENT PROVIDED PARAMETERS
#  Specify in template if desired.

# status, if present, should map to a string value like "200 OK" specifying the http status
STATUS = "whiff.status"

# if present, should map to a list of pairs of strings of headers to add to the http headers
HEADERS = "whiff.headers"

# content type for page: should map to content type like text/html
CONTENT_TYPE = "whiff.content_type"

# top level filter flag (true or false, default true)
DO_FILTER = "whiff.filter"

# directive to parse cgi parameters flags (true or false, default false)
PARSE_CGI = "whiff.parse_cgi"
PARSE_CGI_GET = "whiff.parse_cgi_get"
PARSE_CGI_POST = "whiff.parse_cgi_post"

# cgi require prefix for this fragment
CGI_PREFIX = "whiff.cgi_prefix"

# flag: if true then remove all white head and tail from page streams
STRIP = "whiff.strip"

# a name passed as an environment require for miscellaneous uses (eg, ifdef)
NAME = "whiff.name"

# accessor utility for NAME
def getName(env, n=None):
    "return name relative to cgi_prefix"
    if n is None:
        n = env.get(NAME)
    p = env.get(FULL_CGI_PREFIX)
    if p is None:
        return n
    if n is None:
        return p
    return p+n

def cgiGet(env, name, default=None, strict=True):
    "get cgi variable by relative name (like cgi-get but in python): returns single match or default"
    dict = env.get(CGI_DICTIONARY)
    if dict is None:
        if strict:
            raise ValueError, "cannot get cgi name before cgi parameters have been parsed "+repr(name)
        return None
    #fullname = getName(env, name) # this is wrong because the cgi_dict has already been filtered to remove the prefix
    results = dict.get(name)
    if not results:
        return default
    elif len(results)>1 and strict:
        raise ValueError, "ambiguous cgi name "+repr((name, results))
    return results[0]

def cgiPut(env, name, value):
    dict = env.get(CGI_DICTIONARY)
    if dict is None:
        raise ValueError, "cannot put cgi before cgi parameters have been parsed "+repr(name)
    dict[name] = [value]

def getId(env, name=None, default=None):
    "similar to {{get-id name}}default{{/get-id}} but for python programs"
    relative_name = getName(env, name)
    return env.get(relative_name, default)

def setId(env, name, value):
    "similar to {{set-id name}}value{{/set-id}} but for python programs (in place side-effect to env)"
    relative_name = getName(env, name)
    env[relative_name] = value

def absPath(env, relativePath):
    """
    Get the absolute url path to a component given a path
    relative to the calling WHIFF component.  For example if caller is at
    /xxx/yyy/zzz and relative path is "../www.js" then result should
    be /xxx/www.js
    """
    root = env[ROOT]
    # script name gives path to caller (possibly reset).
    script_name = env["SCRIPT_NAME"]
    # if no script name use entry point
    if not script_name:
        script_name = env[ENTRY_POINT]
    script_path = script_name.split("/")
    #script_path = env.get(whiffenv.TEMPLATE_PATH)
    #pr "resolving (relativePath, script_path)", (relativePath, script_path)
    result = root.absolute_path(relativePath, script_path)
    if relativePath.endswith("/") and not result.endswith("/"):
        result += "/"
    #pr "result is", result
    return result

####################
# DERIVED PARAMETERS
#   Automatically generated under certain circumstances.


# the highest whiff level root resolver
ROOT = "whiff.root"

# the resource monitor for the current request
RESOURCES = "whiff.resources"

# list of path components used for locating relevant configuration template
TEMPLATE_PATH = "whiff.template_path"

# string url pointing back to the most recent whiff configuration template
TEMPLATE_URL = "whiff.template_url"

# numeric timestamp (for forcing image reloads, eg).
TIME_STAMP = "whiff.time_stamp"

# flag set when an error filter has been set
ERROR_WRAPPER = 'whiff.error_wrapper'

# the first HTTP path entering the WHIFF page before modification
# (for example for use in form actions).
ENTRY_POINT = "whiff.entry_point"

# responding path list and path remainder list
RESPONDING_PATH = "whiff.responding_path"
PATH_REMAINDER = "whiff.path_remainder"

# xxxx the following two were added specifically to support repoze.who
# server relative path to top level application (analogous to cgi/SCRIPT_NAME)
APP_PATH = "whiff.app_path"

# server path components left over after locating the top level application (analogous to cgi/PATH_INFO)
APP_PATH_INFO = "whiff.app_path_info"
# xxxx end of adds for repoze.who

# cgi require dictionary, if present
CGI_DICTIONARY = "whiff.cgi"

# top level cgi dictionary before naming transformations
TOP_CGI_DICTIONARY = "whiff.top_cgi"

# source path information 
SOURCE_PATH = "whiff.source_path"

# complete cgi prefix (including parents)
FULL_CGI_PREFIX = "whiff.full_cgi_prefix"

# Security mark in environment when a template has been passed from an external host
# (expandPostedTemplate, for example)
# Apps should check this when doing dangerous things like executing arbitrary database
# queries or changing password.  If the environment is tainted, don't do dangerous things!
# Apps may also "untaint" an environment if they are certain all is well.
#
RPC_TAINTED = "whiff.rpc_tainted"

def mark_rpc_tainted(env):
    env = env.copy()
    env[RPC_TAINTED] = True
    return env

def unmark_rpc_tainted(env):
    env = env.copy()
    env[RPC_TAINTED] = False
    return env

def rpc_tainted(env):
    return env.get(RPC_TAINTED) == True

class SecurityError(RuntimeError):
    "Whiff environment security violation"

def untainted(env):
    if env.get(RPC_TAINTED):
        raise SecurityError("security error: cannot execute with rpc-tainted environment")

def get_valid_keys():
    g = globals()
    valid_keys = {}
    for var in g.keys():
        val = g[var]
        if type(val) is types.StringType and val.startswith("whiff."):
            valid_keys[val] = var
    return valid_keys

VALID_KEYS = get_valid_keys()

class BadEnvironmentName(ValueError):
    "no such whiff environment entry implemented"

def check_environment_message(env):
    te = type(env)
    if not te is types.DictType:
        return (False, "environment must be dictionary, not "+te.__name__)
    for k in env.keys():
        # check environment entries with one dot starting whiff.x -- they should be listed in this module (whiff.x.y might be ok).
        if k.startswith("whiff.") and len(k.split("."))<3:
            test = VALID_KEYS.get(k)
            if test is None:
                return (False, "unknown whiff environment require "+repr((k,VALID_KEYS.keys())))
            #pr "   require", k, "ok"
    return (True, "environment ok") # a-ok

def check_environment(env):
    (test, message) = check_environment_message(env)
    if not test:
        raise BadEnvironmentName, message
    return message

# other misc constants

# the types other than strings recognized as json components
JSON_TYPES = [types.TupleType, types.DictType, types.ListType,
              types.BooleanType, types.IntType, types.FloatType, types.NoneType]


def isAString(x):
    return isinstance(x, str) or isinstance(x, unicode)

# for testing

def myupdate(targetdict, otherdict):
    for (a,b) in otherdict.items():
        b2 = targetdict.get(a)
        if not(b2 is None or b==b2):
            print; # testing output
            print "========== UPDATE ANOMALY========"
            print;print "a", a
            print "b";print b
            print "b2";print b2
            print
            assert a=="captcha_error" or b2 is None or b==b2, "test ASSERT "+repr((a,b,b2))
        targetdict[a] = b
    return targetdict
