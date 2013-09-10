"""
This modules includes all the functions that are used very frequently
and used by multiple modules.
"""

import os
import sys
import shutil
import re
import subprocess

if sys.version_info >= (3, 0):
    from urllib.error import URLError
    from urllib.error import HTTPError
    from urllib.request import urlopen
else:
    from urllib2 import URLError
    from urllib2 import HTTPError
    from urllib2 import urlopen

class MissingToolError(StandardError):
    """
    Will be thrown if GNU make or
    python (2.x) is missing.
    """
    pass

class NoSuchVersionError(StandardError):
    """
    Will be thrown if shared.valid_version_string() returns
    False.
    """
    pass

def get_nodevers_prefix():
    """
    Return the path where Nodes will be installed
    and configuration will be created.
    """
    nodevers_prefix = os.getenv("NODEVERS_PREFIX")
    if nodevers_prefix is not None:
        return nodevers_prefix
    elif os.geteuid() == 0:
        return "/opt/nodevers"
    else:
        home_path = os.getenv("HOME")
        return os.path.join(home_path, ".nodevers")

def valid_nodevers_prefix(path):
    """
    Check if path exists and if it has the required subdirs:
        versions/
        tmp/
        patches/
        patches/global
    """
    dirs = ["versions", "tmp", "patches", os.path.join("patches", "global")]
    for i in dirs:
        full_path = os.path.join(path, i)
        if not os.path.isdir(full_path):
            return False
    return True

def mknodevers_prefix(path):
    """
    Removes the path if it exists and then creates the directories
    needed by nodevers.
    """
    if os.path.exists(path):
        shutil.rmtree(path)
    dirs = ["versions", "tmp", "patches", os.path.join("patches", "global")]
    for i in dirs:
        full_path = os.path.join(path, i)
        os.makedirs(full_path)

def valid_version_string(ver):
    """
    Uses get_remote_versions_list() to see if ver is a valid version.
    """
    if ver in get_remote_versions_list():
        return True
    else:
        return False

def get_versions_dir():
    """
    Return the path where Nodes will be installed.
    """
    return os.path.join(get_nodevers_prefix(), "versions")

def get_bin_dir():
    """
    Return the path where the symlink to current Node's bin
    will be created.
    """
    return os.path.join(get_nodevers_prefix(), "bin")

def get_patches_dir():
    """
    Return the path where the user should put his patches in.
    """
    return os.path.join(get_nodevers_prefix(), "patches")

def get_tmp_dir():
    """
    Return the path where nodevers will download source packages
    and build Node.
    """
    return os.path.join(get_nodevers_prefix(), "tmp")

def get_version_dir(ver):
    """
    Return the path where version should be installed.
    """
    return os.path.join(get_versions_dir(), ver)

def get_real_version_dir(ver):
    """
    Same as get_version_dir() except return None if the path doesn't exist.
    """
    if version_exists(ver):
        return get_version_dir(ver)
    else:
        return None

def version_exists(ver):
    """
    Checks if version is installed.
    """
    version_dir = get_version_dir(ver)
    if os.path.isdir(version_dir):
        return True
    else:
        return False

def get_patches_list(ver):
    """
    Return a list of patches that should be applied to the Node source code.
    """
    patches_list = []
    global_patch_dir = os.path.join(get_patches_dir(), "global")
    version_patch_dir = os.path.join(get_patches_dir(), ver)
    for patch in os.listdir(global_patch_dir):
        full_path = os.path.join(global_patch_dir, patch)
        if not os.path.isdir(full_path):
            patches_list.append(full_path)
    if os.path.isdir(version_patch_dir):
        for patch in os.listdir(version_patch_dir):
            full_path = os.path.join(version_patch_dir, patch)
            if not os.path.isdir(full_path):
                patches_list.append(full_path)
    return patches_list

def _try_python(python_exe):
    """
    Check if python is OK for building Node
    If it is, return True.
    If it is not, return False.
    """
    # Node supports building only with Python 2.6 or 2.7
    try:
        regex = "Python (2\.[67]\.\d+)"
        devnull = open(os.devnull, "w")
        process = subprocess.Popen([python_exe, "-V"], stderr=subprocess.PIPE,
                stdout=devnull)
        ver = process.stderr.read()
        if re.match(regex, ver) is None:
            return False
        else:
            return True
    except OSError:
        return False
    finally:
        devnull.close()

def _try_make(make_exe):
    """
    Check if make is GNU make.
    If it is, return True.
    Otherwise return False.
    """
    try:
        regex = "GNU [Mm]ake"
        devnull = open(os.devnull, "w")
        process = subprocess.Popen([make_exe, "-v"], stdout=subprocess.PIPE)
        ver = process.stdout.read()
        if re.match(regex, ver) is None:
            return False
        else:
            return True
    except OSError:
        return False
    finally:
        devnull.close()

def python():
    """
    Return the python executable that will be used to execute configure.
    """
    pythons = ["python", "python2"]
    for p in pythons:
        if _try_python(p):
            return p
    raise MissingToolError("python is either missing, newer than 2.x or older than 2.6")

def gmake():
    """
    Return the make executable that will be used to build Node.
    """
    makes = ["make", "gmake"]
    for m in makes:
        if _try_make(m):
            return m
    raise MissingToolError("make is either missing or not GNU make")

def help_func(help_str):
    """
    Prints help_str and then
    exits.
    """
    # More Python 2.5/3.x portable than print.
    sys.stdout.write(help_str)
    sys.exit(0)

def link_to(ver):
    """
    Create a symlink to the specified Node's
    bin dir in nodevers prefix.
    """
    if ver == "system":
        if os.path.lexists(get_bin_dir()):
            os.unlink(get_bin_dir())
    elif version_exists(ver):
        if os.path.lexists(get_bin_dir()):
            os.unlink(get_bin_dir())
        version_bin_dir = os.path.join(get_version_dir(ver),
                "bin")
        os.symlink(version_bin_dir, get_bin_dir())
    else:
        raise NoSuchVersionError("no such version installed")

def current_version():
    """
    Try to get the current version.
    """
    # We'll let parse() handle the exceptions.
    process = subprocess.Popen(["node", "-v"], stdout=subprocess.PIPE)
    node_output = process.stdout.read()
    regex = "v(\d+\.\d+\.\d+)"
    match = re.match(regex, node_output)
    ver = match.group(1)
    return ver

def get_remote_versions_list():
    """
    Try to get a list of all the installable Node versions.
    """
    try:
        remote_versions = []
        req = urlopen("http://nodejs.org/dist/")
        data = req.read()
        temp_list = re.findall("\d+\.\d+\.\d+", data)
        for t in temp_list:
            if t in remote_versions:
                pass
            elif re.match("0\.[0-4]\.\d+", t):
                pass
            elif t == "0.5.0":
                pass
            else:
                remote_versions.append(t)
        return remote_versions
    except HTTPError:
        raise HTTPError("cannot download the remote versions list")
    except URLError:
        raise URLError("cannot download the remote versions list")

