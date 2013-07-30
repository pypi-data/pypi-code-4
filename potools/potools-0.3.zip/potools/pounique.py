from optparse import OptionParser
from collections import defaultdict
import logging
import polib
import sys
import os

log = logging.getLogger(__name__)


def parse_options(args=None, values=None):
    usage = "%prog [options] FILE1 FILE2 ..."
    parser = OptionParser(usage)
    parser.add_option("-s", "--sort",
                      action="store_true", dest="sort", default=False,
                      help="Sort output on msgid")
    parser.add_option("-b", "--best-match",
                      action="store_true", dest="best", default=False,
                      help='Choose the "best" msgstr instead of the last.')
    parser.add_option("-o", "--output",
                      dest="output", default=None,
                      help='Output file or directory. Defaults to standardout.')

    (options, args) = parser.parse_args(args, values)
    if len(args) < 2:
        parser.error(u"You have to name two or more po files or directories")
    return (options, args)

def msgstr_sortkey(msg):
    return 'fuzzy' not in msg.flags, len(msg.msgstr)

class PoUnique(object):
    """ Compare two or more po files and generate a po merged po file with no duplicate entries. 
    
        With conflicting entries non-fuzzy will take precedence over fuzzy,
        and then the longest message win.

        Output is printed to stdout, in the format as a valid po file, so that
        it can be sent to translator.
    """

    def __init__(self, args=(), options={}):
        self.options = options
        self.args = [os.path.normpath(path) for path in args]

        # Check if arguments are files or directories.
        argtypes = [os.path.isdir(path) for path in args]
        if any(argtypes) and not all(argtypes):
            raise ValueError('Arguments must all be files or all be directories.')
        
        # Check the output option:
        if options.output is None:
            self.isdir = False
        elif not os.path.exists(options.output) and all(argtypes):
            self.isdir = True
            log.info('Output directory does not exist, and will be created')
        else:
            self.isdir = os.path.isdir(options.output)        

        if any(argtypes) and not self.isdir:
            raise ValueError('When inputs are directories, the output must also be a directory.')
                    

    def run(self):
        """ """
        for path, comparisons in self._get_all_comparisons():
            po = self._make_unique_po(comparisons)
            
            if not self.options.output:
                print po
            elif self.isdir:
                outpath = os.path.join(self.options.output, path)
                dirpath = os.path.split(outpath)[0]
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)
                po.save(outpath)
            else:
                po.save(self.options.output)
                
        sys.exit(0)
        
    def _get_all_comparisons(self):
        if not self.isdir:
            yield '', self.args
        
        for path in self._get_all_unique_paths():
            comparisons = []
            for dirpath in self.args:
                filepath = os.path.join(dirpath, path)
                if os.path.isfile(filepath):
                    comparisons.append(filepath)
            if comparisons:
                yield path, comparisons
        
    def _get_all_unique_paths(self):
        all_paths = set()
        for path in self.args:
            prefix_len = len(path) + 1
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if os.path.splitext(filename)[1] == '.po':
                        filepath = os.path.join(dirpath, filename)
                        all_paths.add(filepath[prefix_len:])
        return all_paths
                        
        
    def _make_unique_po(self, filepaths):
        unique_entries = self._get_unique(filepaths)
        return self._generate_pofile(unique_entries, filepaths[0])

    def _get_unique(self, filepaths):
        all_entries = defaultdict(list)
        entry_order = []
        for path in filepaths:
            po = polib.pofile(path)
            for entry in po:
                if entry.msgid not in all_entries:
                    entry_order.append(entry.msgid)
                all_entries[entry.msgid].append(entry)
            
        if self.options.sort:
            entry_order = sorted(entry_order, key = lambda x: x.lower())
        for k in entry_order:
            v = all_entries[k]
            if self.options.best:
                yield sorted(v, key=msgstr_sortkey)[-1]
            else:
                yield v[-1]
            
    def _generate_pofile(self, entries, headerfile):
        outpo = polib.POFile()
        headerpo = polib.pofile(headerfile)
        # Copy header and metadata
        outpo.header = headerpo.header
        for (key, val) in headerpo.metadata.items():
            outpo.metadata.update({key: val})
        for e in entries:
            outpo.append(e)
        return outpo


def main():
    """ """
    options, args = parse_options()
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s")
    pogetnew = PoUnique(args, options)
    pogetnew.run()
