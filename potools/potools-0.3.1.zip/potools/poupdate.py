from optparse import OptionParser
from potools import utils
import logging
import polib
import os
import time
import datetime

log = logging.getLogger(__name__)

def po_timestamp():
    tzminutes = [time.timezone, time.altzone][time.daylight] // 60
    # Apparently PO files use POSIX standard times, where timezones
    # are backwards, hence the minus:
    tzstr = '%+03d%02d' % divmod(-tzminutes, 60)
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M') + tzstr

def parse_options(args=None, values=None):
    usage = "%prog [options] TARGET SOURCE"
    parser = OptionParser(usage)
    parser.add_option("-n", "--insert-new",
                      action="store_true", dest="insert_new", default=False,
                      help="Insert msgid's from the SOURCE that do not exist in TARGET")
    parser.add_option("-f", "--force",
                      action="store_true", dest="force", default=False,
                      help="Always overwrite the TARGET msgstr even if the SOURCE msgstr is empty or fuzzy")
    parser.add_option("-u", "--use-fuzzy",
                      action="store_true", dest="use_fuzzy", default=False,
                      help="Insert msgid's from the SOURCE even though they are fuzzy, if TARGET is empty")
    parser.add_option(
        "-r", "--reset-fuzzy",
        action="store_true", dest="reset_fuzzy", default=False,
        help="Remove an existing fuzzy flag on translations in the target "
        "when they get updated.")

    (options, args) = parser.parse_args(args, values)
    if len(args) < 2:
        parser.error(u"You have to name two po-files or directories of po-files")
    return (options, args)


class PoUpdate(object):
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
            raise ValueError('Arguments must both be files or both be directories.')

        self.isdir = any(argtypes)

    def run(self):
        """ """
        # Target is the po file that should be updated.
        # Source is the one with new translations.
        target, source = self.args
        if not self.isdir:
            self._update_po(target, source)
        else:
            prefix_len = len(source) + 1
            for dirpath, dirnames, filenames in os.walk(source):
                for filename in filenames:
                    if os.path.splitext(filename)[1] == '.po':
                        source_path = os.path.join(dirpath, filename)
                        relative_path = source_path[prefix_len:]
                        target_path = os.path.join(target, relative_path)
                        if os.path.exists(target_path):
                            self._update_po(target_path, source_path)


    def _update_po(self, target_path, source_path):
        log.info("Updating %s from %s" % (target_path, source_path))
        target = polib.pofile(target_path)
        source = polib.pofile(source_path)

        target_dict = {}
        for entry in target:
            target_dict[entry.msgid] = entry

        count = 0
        for entry in source:
            if not entry.msgid in target_dict:
                if self.options.insert_new:
                    # If it's not in the target and -n is true, add it:
                    target.append(entry)
                continue
            target_entry = target_dict[entry.msgid]
            if target_entry.msgstr != entry.msgstr:
                # The messages are different. Check if we should update.
                if not self.options.force:
                    # if force is set, skip the checks and always update.
                    if not entry.msgstr:
                        # The new message is empty, we should not update
                        continue
                    if not utils.msg_is_updated(entry):
                        # The new message is fuzzy
                        if utils.msg_is_updated(target_entry):
                            # the old message is not fuzzy and not empty
                            continue
                        elif not self.options.use_fuzzy:
                            # Never use fuzzy unless use_fuzzy is set:
                            continue
                # Update the target
                target_dict[entry.msgid].msgstr = entry.msgstr
                # Since the target has been updated with a new translation,
                # it is no longer fuzzy
                if self.options.reset_fuzzy and \
                        'fuzzy' in target_dict[entry.msgid].flags:
                    target_dict[entry.msgid].flags.remove('fuzzy')
                count += 1

        if not count:
            log.info("No entries updated")
            return

        # Update the revision date.
        source_date = source.metadata.get('PO-Revision-Date', '')
        target_date = target.metadata.get('PO-Revision-Date', '')
        if source_date > target_date:
            # In this case we use the source date as the last update
            target.metadata['PO-Revision-Date'] = source_date
        else:
            # The target has been modified after the source.
            # We set the revision date to now, to mark it as changed.
            target.metadata['PO-Revision-Date'] = po_timestamp()
        target.save(target_path)
        log.info("%s entries updated" % count)


def main():
    """ """
    options, args = parse_options()
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s")
    pogetnew = PoUpdate(args, options)
    pogetnew.run()
