
from distutils.core import setup, Extension 

import os
import sys
import platform

# Get the script directory.
def get_script_dir():
    path = os.path.abspath(sys.argv[0])
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

# set platform var
os_type = ''
arch_type = ''

if platform.system() == 'Windows':
    os_type = 'Windows'

    if platform.architecture()[0] == '32bit':
        arch_type = 'x86'
    elif platform.architecture()[0] == '64bit':
        arch_type = 'x64'
    else:
        print('The machine type cannot be determined. Exit.')
        sys.exit(1)

elif platform.system() == 'Linux':
    os_type = 'Linux'

    if platform.architecture()[0] == '32bit':
        arch_type = 'x86'
    elif platform.architecture()[0] == '64bit':
        arch_type = 'x64'
    else:
        print('The machine type cannot be determined. Exit.')
        sys.exit(1)
else:  # Other OS: MAC OS X, AIX ...
    pass

# set Include dir and Link dir
inc_dir = ''
lnk_dir = ''

if os_type == 'Windows':
    script_dir = get_script_dir()

    inc_dir = os.path.join(script_dir, "cci\\include")
    if arch_type == 'x86':
        lnk_dir = os.path.join(script_dir, "cci\\lib\\win")
    else:
        lnk_dir = os.path.join(script_dir, "cci\\lib64\\win")

elif os_type == 'Linux':
    script_dir = get_script_dir()

    inc_dir = os.path.join(script_dir, "cci/include")
    if arch_type == 'x86':
        lnk_dir = os.path.join(script_dir, "cci/lib/linux")
    else:
        lnk_dir = os.path.join(script_dir, "cci/lib64/linux")

else:
    try:
        if os.environ["CUBRID"]:
            lnk_dir = os.environ["CUBRID"] + "/lib"
            inc_dir = os.environ["CUBRID"] + "/include"
    except KeyError:
        raise KeyError('CUBRID environ variable not set.')

# set ext_modules
if os_type == 'Windows':
    if os.path.isfile(os.path.join(lnk_dir, 'cas_cci.lib')):  # use the CCI static library
        ext_modules = [
            Extension(
                name = "_cubrid", 
                extra_link_args = ["/NODEFAULTLIB:libcmt"],
                library_dirs = [lnk_dir],
                libraries = ["cas_cci", "libregex38a", "ws2_32", "oleaut32", "advapi32"],
                include_dirs = [inc_dir],
                sources = ['python_cubrid.c'],
            )
        ]
    else:
        print("CCI static lib not found. Exit.")
        sys.exit(1)

elif os_type == 'Linux':
    cci_static_lib = os.path.join(lnk_dir, 'libcascci.a')
    if os.path.isfile(cci_static_lib):  # use the CCI static library
        ext_modules = [
            Extension(
                name = "_cubrid", 
                include_dirs = [inc_dir],
                sources = ['python_cubrid.c'],
                libraries = ["pthread", "stdc++"],
                extra_objects = [cci_static_lib]
            )
        ]
    else:
        print("CCI static lib not found. Exit.")
        sys.exit(1)

else:
    cci_static_lib = os.path.join(lnk_dir, 'libcascci.a')
    if os.path.isfile(cci_static_lib):  # use the CCI static library
        ext_modules = [
            Extension(
                name = "_cubrid", 
                include_dirs = [inc_dir],
                sources = ['python_cubrid.c'],
                libraries = ["pthread", "stdc++"],
                extra_objects = [cci_static_lib]
            )
        ]
    else:  # use CCI dynamic library
        ext_modules = [
            Extension(
                name = "_cubrid", 
                library_dirs = [lnk_dir],
                libraries = ["cascci"],
                include_dirs = [inc_dir],
                sources = ['python_cubrid.c'],
            )
        ]
        
# set py_modules
if sys.version_info[0] == 2 and sys.version_info[1] >= 5:
    py_modules = [
        "CUBRIDdb.connections", "CUBRIDdb.cursors", "CUBRIDdb.FIELD_TYPE",
        "django_cubrid.base", "django_cubrid.client", "django_cubrid.compiler", 
        "django_cubrid.creation", "django_cubrid.introspection", "django_cubrid.validation",
        ]
else:
    py_modules = ["CUBRIDdb.connections", "CUBRIDdb.cursors", "CUBRIDdb.FIELD_TYPE"]
    
# Install CUBRID-Python driver.
setup(
    name = "CUBRID-Python", 
    version = "9.1.0.0001",
    description = "Python interface to CUBRID",
    long_description = \
            "Python interface to CUBRID conforming to the python DB API 2.0 "
            "specification.\n"
            "See http://www.python.org/topics/database/DatabaseAPI-2.0.html.",
    py_modules = py_modules,
    author = "Li Jinhu, Li Lin, Zhang hui",
    author_email = "beagem@nhn.com",
    license = "BSD",
    url = "http://svn.cubrid.org/cubridapis/python/",
    ext_modules = ext_modules
)


