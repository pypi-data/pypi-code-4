#!/usr/bin/env python3

from tempfile import mkstemp
from shutil import move
from os import remove, close
import re, sys, pdb

from tempfile import mkstemp

setup_version_pattern = r"(\w+=')(\d+.\d+.)(\d+)('.*)"

#### INTERFACE

def increment_version(setup_file="./setup.py", overwrite=True):
    new_file = replace(setup_file, process_line, overwrite)
    return new_file

def get_version(setup_file="./setup.py"):
    contents = open(setup_file).read()        
    match = re.search(setup_version_pattern, contents)
    return match.group(2) + match.group(3)

#### HELPERS

def inc_version(version):
    match = re.search(setup_version_pattern, version)
    if not match:
        strng = "Could not understand version number: " + version
        strng += ".  Should be format: version='1.2.45'"
        print( strng )
        raise Exception(strng)
    final_num = int(match.group(3))
    return match.group(1) + match.group(2) + str(final_num + 1) + match.group(4) + "\n"

def process_line(line):
    match = re.search(setup_version_pattern, line)
    if not match:
        return line
    new_line = inc_version(line)
    return new_line

def replace(src_file_path, process_line, overwrite):
    #Create temp file
    fh, new_file_path = mkstemp()
    new_file = open(new_file_path,'w')
    old_file = open(src_file_path)
    for line in old_file:
        new_file.write(process_line(line))
    # pdb.set_trace()
    new_file.flush()
    new_file.close()
    close(fh)
    old_file.close()
    if overwrite:
        remove(src_file_path)
        move(new_file_path, src_file_path)
    return new_file_path

######## TESTS

def _test():
    test_inc_version()
    test_process_line()
    test_increment_version()
    test_get_version()

def test_get_version():
    setup_file = "./test_setup.py"
    version = get_version(setup_file)
    assert version == "0.1.1"

def test_increment_version():
    setup_file = './test_setup.py'
    newfile = increment_version(setup_file, overwrite=False)
    assert "version='0.1.2'" in open(newfile).read()        
    remove(newfile)

def test_inc_version():
    ver = "version='1.3.4'\n"
    incd_ver = inc_version(ver)
    assert incd_ver == "version='1.3.5'\n"

def test_process_line():
    real_line = "version='1.2.3'\n"
    incd_ver = process_line(real_line)
    assert incd_ver == "version='1.2.4'\n"
    other_line = "abc123"
    incd_ver = process_line(other_line)
    assert incd_ver == other_line

if __name__ == '__main__':
    _test()
