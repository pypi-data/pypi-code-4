"""
This module defines the following function generators:

  - file_finder(): it looks for files whose names match with a given pattern. For example, 
    this code searches for a file called `os.py`:

        >>> for file in file_finder('os.py', os.path.dirname(os.__file__)):
        ...     print(os.path.basename(file)) # Print just the file name, not its full path 
        ...     
        ... 
        os.py

    By looking for files in the `os` module directory, it finds the `os.py` file.

  - file_inspector(): it looks inside a file for a given pattern. Here is an example: 
      
        >>> for match in file_inspector(doctest.__file__, 'Tim Peters'):
        ...     print(match, end='')
        ...     
        ... 
        # Released to the public domain 16-Jan-2001, by Tim Peters (tim@python.org).

"""

import fnmatch
import os
import re

def file_finder(pattern: str, top_dir: str=os.curdir, recursive: bool=False):
    """Look for files whose names match with a given pattern and return a generator.

    If no specified directory is given, it searches inside the current directory: 
    
        >>> for file in file_finder('pyfinder.py'):
        ...     print(os.path.basename(file))
        ...     
        ... 
        pyfinder.py
    
    A second optional argument allows us to indicate the top directory:

        >>> for file in file_finder('message.py', os.path.dirname(email.__file__)):
        ...     print(os.path.basename(file))
        ...     
        ... 
        message.py

    It is possible to use a pattern with Unix shell-style wildcards:

        >>> for file in file_finder('me*age.py', os.path.dirname(email.__file__)):
        ...     print(os.path.basename(file))
        ...     
        ... 
        message.py

    A third optional argument is used in order to perform (True) or not (False) a recursive research:

        >>> for file in file_finder('me*age.py',  os.path.dirname(email.__file__), True):
        ...     print(os.path.basename(file))
        ...     
        ... 
        message.py
        message.py

    In the example above, it twice found `message.py`: the first one is inside the `email` directory of 
    the standard library, while the second one is inside the `mime` sub-directory.
    """
    for path, dirs, files in os.walk(top_dir):
        if not recursive: 
            dirs.clear() # Clear the `top_dir` sub-directories list
        for name in fnmatch.filter(files, pattern):
            yield os.path.join(path, name)


def file_inspector(file_name: str, pattern: str):
    """Look inside a file for a given pattern and return a generator.

    The code below searches inside the module `re` for the text `Regular`:

        >>> for match in file_inspector(re.__file__, 'Regular'):
        ...     print(match, end='')
        ...     
        ... 
        # Secret Labs' Regular Expression Engine
        Regular expressions can contain both special and ordinary characters.

    It is possible to use regular expressions:

       >>> for match in file_inspector(re.__file__, '^Regular'):
       ...     print(match, end='')
       ...     
       ... 
       Regular expressions can contain both special and ordinary characters.
        
    """
    for line in open(file_name):
        if re.search(pattern, line):
            yield line


if __name__ == '__main__':
    import doctest, email
    doctest.testmod()
