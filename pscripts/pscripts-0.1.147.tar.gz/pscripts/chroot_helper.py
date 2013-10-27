#!/usr/bin/env python

from subprocess import check_output, call

def copy_exe(bin, chroot_jail, side_effects=True):
    chroot_jail = trim_trailing_slash(chroot_jail)
    cmd = "ldd `which {}`".format(bin)
    output = check_output(cmd, shell=True)
    dependencies = output.decode("utf-8").split("\n")
    clean_deps = []
    for dep in dependencies:
        parts = dep.split(" ")
        for part in parts:
            if part.find("/") >= 0:
                clean_deps.append(part.strip())
    for dep in clean_deps:
        cmd = ["cp", dep, chroot_jail + dep]
        if side_effects:
            call(cmd)
        else:
            print(" ".join(cmd))

def trim_trailing_slash(arg):
    if arg[-1:] == "/":
        return arg[:-1]
    return arg

def _test():
    copy_exe("bash", "/chroot_jail/", side_effects=False)
    assert "abc" == trim_trailing_slash("abc/")    
    assert "abc" == trim_trailing_slash("abc")    

if __name__ == '__main__':
    _test()
    
