import logging
import os
import re

from _dd_interface import DrivenDoc
from _dd_interface import PRE_CONFIG, CONFIG, POST_CONFIG
from _dd_interface import PREDICT, POST_PREDICT, RESPONSE, POST_RESPONSE
from _dd_interface import RUNTIME, POST_RUNTIME, REPORT, POST_REPORT


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_docdriven_interface(doc_filepath, debug_output=None):
    print_feed=False
    line_feed=False
    file_feed=False
    if debug_output is None:
        pass
    elif debug_output == 'line_feed':
        line_feed=True
    elif debug_output == 'file_feed':
        file_feed=True
    elif debug_output == 'file_line_feed':
        print_feed=True
    else:
        log.debug('Unrecognized debug_output selection: '+str(debug_output))
        log.debug('Must be one of: "line_feed", "file_feed", or "file_line_feed"')
        log.debug('continuing with no debug_output')
        pass

    if print_feed:
        log.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ dd feed @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    root_dir, basename = os.path.split(doc_filepath)
    driven_doc = DrivenDoc(root_dir, basename)
    feed_file(driven_doc, doc_filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl=0)
    if print_feed:
        log.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    return driven_doc


link_to_file_pattern = '(^%# (\w+.*)|^#### ((config|predict|response|runtime|report)/\w+.*))'
regex = re.compile(link_to_file_pattern)
def feed_file(driven_doc, filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl=0):
    # log.debug('feed_file-filepath: '+filepath)
    # log.debug('feed_file-root_dir: '+root_dir)
    full_filepath = os.path.join(root_dir, filepath)
    if file_feed:
        log.debug(full_filepath)
    filename = os.path.basename(full_filepath)
    from_filekey = filename[:filename.rfind('.')] # last index of .
    feeder_file = open(full_filepath, 'r')
    for line in feeder_file:
        line = line.rstrip()
        # A line that starts with '!' is considered commented-out
        if line.startswith('!'):
            continue

        match = regex.search(line)
        if match:
            # print match.groups()
            path = match.groups()[1] if match.groups()[1] and len(match.groups()[1]) > 0 else match.groups()[2]
            if print_feed:
                log.info(' '*(4*rcrsn_lvl)+'+---+    '+line)
            if not path.startswith(('config/', 'predict/', 'response/', 'runtime/', 'report/', 'chapter/')):
                raise Exception('cannot import from unrecognized location: '+path)
            if not path.endswith(('.json', '.py', '.dd')):
                raise Exception('cannot import unrecognized filetype: '+path)
            if not path.startswith('chapter/'):
                path = 'chapter/'+path
            include_filepath = os.path.join(root_dir, path)
            if match.groups()[3] is not None:
                feed_line(driven_doc, ('#### '+match.groups()[3]+'\n'), from_filekey, line_feed, print_feed, rcrsn_lvl+1)
                if match.groups()[3] == 'runtime':
                    feed_line(driven_doc, ('~'*42)+'  python\n', from_filekey, line_feed, print_feed, rcrsn_lvl+1)
                else:
                    feed_line(driven_doc, ('~'*44)+'  json\n', from_filekey, line_feed, print_feed, rcrsn_lvl+1)
                feed_file(driven_doc, include_filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl+1)
                feed_line(driven_doc, ('~'*50)+'\n', from_filekey, line_feed, print_feed, rcrsn_lvl+1)
            else:
                feed_file(driven_doc, include_filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl+1)
        else:
            feed_line(driven_doc, line, from_filekey, line_feed, print_feed, rcrsn_lvl)
    feeder_file.close()

def feed_line(driven_doc, line, from_filekey, line_feed, print_feed, rcrsn_lvl):
    if print_feed:
        log.info(' '*(4*rcrsn_lvl)+'|    '+line.rstrip())
    if line_feed:
        log.debug('|   '+line.rstrip())
    driven_doc.feed_line(line, from_filekey)

def print_to_files(driven_doc, include_response=True):
    # first we calculate what the important directories are
    status_dir = os.path.join(driven_doc.root_dir, 'status/')
    pub_dir = os.path.join(driven_doc.root_dir, 'publish/')

    # we also calculate some of the filenames that we know we will use
    bare_filename = driven_doc.filename[:len(driven_doc.filename)-3]
    log.warning('bare_filename: '+bare_filename)
    status_filename = os.path.join(status_dir, bare_filename+'.status')
    ch_status_filename = os.path.join(status_dir, bare_filename+'.ch.status')
    pre_pdf_all_filename = os.path.join(pub_dir, bare_filename+'.all.dd')

    # first we print the pre-pdf .all.dd file
    pre_pdf_all_file = open(pre_pdf_all_filename, 'w')
    driven_doc.print_all_to_file(pre_pdf_all_file, include_response)
    pre_pdf_all_file.close()

    # then we print the .nav.dd files -- this method call will result in the
    # DrivenDoc creating a filename.nav.dd file in which each chapter is in
    # its own file in the chapter directory and each json/code snippet is in
    # one of the sub-directories of the chapter directory.
    # driven_doc.print_nav_to_file()

    # next we delete the .status files that have this bare_filename.
    # we do this in case they were created the last time we ran the program.
    # this is ugly and I'm embarassed by it.
    delete_file(status_filename)
    delete_file(ch_status_filename)

    # next we print out the fresh .status files
    status_file = open(status_filename, 'w')
    driven_doc.print_status_report(status_file)
    status_file.close()

    ch_status_file = open(ch_status_filename, 'w')
    driven_doc.print_ch_status_report(ch_status_file)
    ch_status_file.close()

def delete_file(full_filepath):
    # I don't remember how I cam up with the horrible technique here
    try:
        os.remove(full_filepath) # delete it if it already existed
    except:
       pass
    open(full_filepath, 'w').close()
    try:
        os.remove(full_filepath) # delete it if it already existed
    except:
       pass


