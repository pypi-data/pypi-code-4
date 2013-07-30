import os
import logging
import polib
from optparse import OptionParser
from potools.utils import get_default

log = logging.getLogger(__name__)

def parse_options(args=None, values=None):
    usage = "%prog [options] SOURCE TARGET"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="Verbose mode")
    parser.add_option("-u", "--update",
                        action="store_true", dest="update", default=False,
                        help="Update original file instead of creating a new file.")
    parser.add_option("-f", "--fuzzy",
                        action="store_true", dest="fuzzy", default=False,
                        help="Force override for all fuzzy entries, even if "
                        "they already contain a translation.")
    (options, args) = parser.parse_args(args, values)
    if options.update and len(args) != 1:
        parser.error(u"When using the -u/--update parameter, you can give only one argument.")
    if not options.update and len(args) != 2:
        parser.error(u"You need a source and target parameter that can either be files or directories.")
    return (options, args)


class PoPopulate(object):
    """ For every untranslated or fuzzy entry, copy its "Default"
        string for its msgstr value. If no default value exists, copy its
        msgid.
    """
    def __init__(self, options, args):
        self.options = options
        self.untranslated = 0
        self.updated = 0
        self.missing = 0

        if self.options.update:
            args = [args[0], args[0]]

        self.args = [os.path.normpath(path) for path in args]

        if os.path.isdir(args[0]):
            self.isdir = True
            if not os.path.exists(args[1]):
                log.info('Output directory does not exist, and will be created')
            else:
                if not os.path.isdir(args[1]):
                    raise ValueError('Arguments must all be files or all be directories.')
        else:
            self.isdir = False
            if os.path.isdir(args[1]):
                raise ValueError('Arguments must all be files or all be directories.')


    def run(self):
        source, target = self.args
        if not self.isdir:
            self._populate(source, target)
        else:
            prefix_len = len(source) + 1
            for dirpath, dirnames, filenames in os.walk(source):
                for filename in filenames:
                    if os.path.splitext(filename)[1] == '.po':
                        source_path = os.path.join(dirpath, filename)
                        relative_path = source_path[prefix_len:]
                        target_path = os.path.join(target, relative_path)
                        target_dir = os.path.split(target_path)[0]
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)
                        self._populate(source_path, target_path)

        log.info("Untranslated entries found: %d" % self.untranslated)
        log.info("Entries updated with default: %d" % self.updated)
        log.info("Untranslated entries with no default: %d" % (self.missing))

    def _populate(self, infile, outfile):
        pofile = polib.pofile(infile)

        modified = False
        for entry in pofile:
            if self.options.fuzzy and 'fuzzy' in entry.flags:
                entry.msgstr = ""
            if not entry.msgstr:
                self.untranslated += 1
                # Empty message string, try to find an update
                default = get_default(entry)
                if not default:
                    self.missing += 1
                else:
                    self.updated += 1
                    modified = True
                    entry.msgstr = default
                    if not 'fuzzy' in entry.flags:
                        entry.flags.append('fuzzy')

        if self.options.update and not modified:
            # Don't save if this is an inplace update and there was no modifications.
            return
        pofile.save(outfile)


def main():
    options, args = parse_options()
    logging.basicConfig(
            level=options.verbose and logging.DEBUG or logging.INFO,
            format="%(levelname)s: %(message)s")
    popopulate = PoPopulate(options, args)
    popopulate.run()

