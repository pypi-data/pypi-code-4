# -*- coding: utf-8  -*-
from __future__ import unicode_literals, print_function
import sys

if sys.version_info[0] == 2:
    range = xrange
loops = 10000
def runner(text, child):
    from mwparserfromhell.parser._tokenizer import CTokenizer
    r1, r2 = range(200), range(loops)
    for i in r1:
        CTokenizer().tokenize(text)
    child.send("OK")
    child.recv()
    child.send("OK")
    child.recv()
    for i in r2:
        CTokenizer().tokenize(text)
    child.send("OK")
    child.recv()

if __name__ == "__main__":
    from os import listdir, path
    from multiprocessing import Process, Pipe
    import locale
    import os
    import sys

    import psutil

    from mwparserfromhell.compat import py3k

    class Memtest(object):

        def __init__(self):
            self.tests = []

        def _load_tests(self, filename, name, text):
            tests = text.split("\n---\n")
            counter = 1
            digits = len(str(len(tests)))
            for test in tests:
                data = {"name": None, "label": None, "input": None, "output": None}
                for line in test.strip().splitlines():
                    if line.startswith("name:"):
                        data["name"] = line[len("name:"):].strip()
                    elif line.startswith("label:"):
                        data["label"] = line[len("label:"):].strip()
                    elif line.startswith("input:"):
                        raw = line[len("input:"):].strip()
                        if raw[0] == '"' and raw[-1] == '"':
                            raw = raw[1:-1]
                        raw = raw.encode("raw_unicode_escape")
                        data["input"] = raw.decode("unicode_escape")
                number = str(counter).zfill(digits)
                fname = "test_{0}{1}_{2}".format(name, number, data["name"])
                self.tests.append((fname, data["input"]))
                counter += 1

        def build(self):
            def load_file(filename):
                with open(filename, "rU") as fp:
                    text = fp.read()
                    if not py3k:
                        text = text.decode("utf8")
                    name = path.split(filename)[1][:0-len(extension)]
                    self._load_tests(filename, name, text)

            directory = path.join(path.dirname(__file__), "tokenizer")
            extension = ".mwtest"
            if len(sys.argv) > 2 and sys.argv[1] == "--use":
                for name in sys.argv[2:]:
                    load_file(path.join(directory, name + extension))
                sys.argv = [sys.argv[0]]  # So unittest doesn't try to load these
            else:
                for filename in listdir(directory):
                    if not filename.endswith(extension):
                        continue
                    load_file(path.join(directory, filename))

    class Color:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        RESET = '\033[0m'

    def print_results(info1, info2):
        r1, r2 = info1.rss, info2.rss
        buff = 8192
        if r2 - buff > r1:
            d = r2 - r1
            p = float(d) / r1
            bpt = d / loops
            sys.stdout.write("{0}LEAKING{1}: {2:n} bytes, {3:.2%} inc ({4:n} bytes/loop)".format(Color.YELLOW, Color.RESET, d, p, bpt))
        else:
            sys.stdout.write("{0}OK{1}".format(Color.GREEN, Color.RESET))

    locale.setlocale(locale.LC_ALL, "")
    tester = Memtest()
    tester.build()
    width = 1
    for (name, _) in tester.tests:
        if len(name) > width:
            width = len(name)
    for (name, text) in tester.tests:
        sys.stdout.write(name.ljust(width) + ": ")
        sys.stdout.flush()
        parent, child = Pipe()
        p = Process(target=runner, args=(text, child))
        p.start()
        try:
            proc = psutil.Process(p.pid)
            parent.recv()
            parent.send("OK")
            parent.recv()
            info1 = proc.get_memory_info()
            sys.stdout.flush()
            parent.send("OK")
            parent.recv()
            info2 = proc.get_memory_info()
            print_results(info1, info2)
            sys.stdout.flush()
            parent.send("OK")
        finally:
            proc.kill()
            print()
