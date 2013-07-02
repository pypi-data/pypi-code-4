from . import __version__
from .sampling import ReservoirSample

import os, subprocess
import sys, logging
def goodbye(message):
    sys.stderr.write('\n')
    sys.stderr.write(message)
    sys.stderr.write('\n')
    sys.stderr.flush()
    sys.exit(0)

if sys.version_info[0] == 3:
    if sys.version_info[1] < 3:
        goodbye("Error: Python >= 3.3 is required for this to work.")
else:
    goodbye("Error: Python >= 3.3 is required for this to work.")

import shutil, random, gzip, pickle
import json, urllib, urllib.request, urllib.parse, urllib.error, http.client
import socket
from collections import namedtuple, OrderedDict
    
try:
    import ngs_plumbing.fastq as fastq
    import ngs_plumbing.parsing
except ImportError:
    goodbye("""
Error: The package 'ngs_plumbing' cannot be imported.
It is available on Pypi, and installing it can be as simple
as running `pip install ngs_plumbing`.
Note: the optional dependency on h5py 
coming with ngs_plumbing is _not_ required.""")

HEADERS = {"User-Agent": "dnasnout-client-v{0}".format(__version__)}


Entry = namedtuple('Entry', 'header sequence quality')

def list_asfasta(lst):
    """ Turn a list of Entry objects into a FASTA string """
    return b'\n'.join(b'\n'.join((b'>'+x.header[1:], x.sequence)) for x in lst)

def avgqual_phred(qualstring):
    """ Average quality in a quality string from Phred scores.
    Return zero (0) if string of length 0. """
    l = len(qualstring)
    if l == 0:
        return 0
    else:
        return sum(ord(x)-33 for x in qualstring) / l

def _message(msg, logger, screen):
    if logger is not None:
        logger.info(msg);
    if screen is not None:
        try:
            screen.stdscr.addstr(screen.y, screen.x, msg,
                                 curses.A_NORMAL)
            screen.stdscr.clrtoeol()
            screen.stdscr.refresh()
        except curses.error:
            pass


def _filter_passthrough(logger, screen, entryname):
    def f(entries):
        count = int(0); inc = int(1)
        for entry in entries:
            yield entry
            if count % 10000 == 0:
                msg = "Read {:,} {:s} entries".format(count, entryname)
                _message(msg, logger, screen)
            count += inc
        msg = "Read {:,} {:s} entries".format(count, entryname)
        _message(msg, logger, screen)
    return f

def _filter_bam(logger, screen):
    """ Filter bam entries """
    LMIN = 32
    PNMAX = 0.05
    AQMIN = 30
    def f(entries):
        count = int(0); inc = int(1)
        for read in entries:
            # filter the read out if either:
            # - already mapped
            # - read length < LMIN
            # - percentage of 'N's in the read > PNMAX
            # - average quality score > AQMIN
            if (not read.is_unmapped) or \
                    (len(read.seq) < LMIN) or \
                    ((1.0 * read.seq.count('N') / len(read.seq)) > PNMAX) or \
                    avgqual_phred(read.qual) > AQMIN:
                pass 
            else:
                yield Entry(read.tags[2][1], read.seq, None) # empty quality
            if count % 10000 == 0:
                msg = "Read {0:,} unmapped BAM entries (l >= {1})".format(count, LMIN)
                _message(msg, logger, screen)
            count += inc
        msg = "Read {0:,} unmapped BAM entries (l >= {1})".format(count, LMIN)
        _message(msg, logger, screen)
    return f

def _sample_entries(entries, spl, entryname = '', screen=None):
    for entry in entries:
        spl.add(entry)
    return count
    
def _tofastq_reads_bam(input_file, output_file):
    LMIN = 32
    PNMAX = 0.05
    AQMIN = 30
    f = pysam.Samfile(input_file.name, "rb")
    count_ok = int(0)
    count_total = int(0)
    inc = int(1)
    for read in f:
        # filter the read out if either:
        # - already mapped
        # - read length < LMIN
        # - percentage of 'N's in the read > PNMAX
        # - average quality score > AQMIN
        count_total += inc
        if (not read.is_unmapped) or \
                (len(read.seq) < LMIN) or \
                ((1.0 * read.seq.count('N') / len(read.seq)) > PNMAX) or \
                avgqual_phred(read.qual) > AQMIN:
            continue
        output_file.writelines(('@'+read.tags[2][1], '\n', read.seq, '\n+\n', read.qual, '\n'))
        if count_total % 10000 == 0:
            sys.stdout.write("\rWrote {0:,}/{1:,} unmapped BAM entries into FASTQ".format(count_ok, count_total));
            sys.stdout.flush()
        count_ok += inc
    sys.stdout.write("\rWrote {0:,}/{1:,} unmapped BAM entries into FASTQ.\n".format(count_ok, count_total));
    sys.stdout.flush()
    f.close()
    return (count_ok, count_total)

FFORMAT_OPENER = OrderedDict((('AUTO', ngs_plumbing.parsing.open),
                              ('FASTQ', fastq.FastqFile), 
                              ('FASTQ.gz', fastq.GzipFastqFile), 
                              ('BAM', None))) #FIXME

def _makeparser():
    _N = 300
    import argparse
    parser = argparse.ArgumentParser(
        description = '''
DNA-snout <pig-noise>, a simple client.

The communication protocol with server is likely to change
without prior notice. Make sure that you are using the latest
version of this script.

By default the script is querying our server "tapir"
(http://tapir.cbs.dtu.dk). This is a relatively modest server,
and one should be gentle with it - hitting it too heavily may
result in having your IP banned.
''',
        epilog = 'Version {0} - Laurent Gautier(2013) <laurent@cbs.dtu.dk, lgautier@gmail.com>'.format(__version__)
        )

    required = parser.add_argument_group('required arguments')
    required.add_argument('-i', '--input-file',
                          required = True,
                          nargs = '+',
                          type = argparse.FileType('rb'),
                          dest = 'input_files',
                          help = 'Input file')
    required.add_argument('-d', '--output-directory',
                          dest = 'out_d',
                          metavar = '<directory>',
                        required = True,
                          help = 'Output directory')
    required.add_argument('-P', '--n-processes',
                          dest = 'n_processes',
                          type = int,
                          default = 1,
                          help = 'Number of processes to use (note: each bowtie instance in a process can itself use several threads) [currently not doing anything useful]')
    optional_files = parser.add_argument_group('optional arguments for files and storage')
    optional_files.add_argument('-f', '--input-format',
                                metavar = '<file format>',
                                dest = 'input_format',
                                choices = FFORMAT_OPENER.keys(),
                                default = 'AUTO',
                                help = 'Input format, as one of {%(choices)s}. If AUTO, an educated guess will be made from the file extension. (default: %(default)s)')
    optional_files.add_argument('--ref-directory',
                                dest = 'refdir',
                                metavar = '<directory>',
                                help = 'Directory in which to find reference sequences and indexes, or add them whenever necessary. This allows to reuse reference sequences and bowtie2 indexes across several DNA sequencing data sets.')
    optional_files.add_argument('-l', '--log-file',
                                dest = 'log_file',
                                metavar = '<file name>',
                                type = argparse.FileType('wb'),
                                help = 'Log file')
    optional_sampling = parser.add_argument_group('optional arguments for the sampling')
    optional_sampling.add_argument('--seed',
                                   dest = 'seed',
                                   default = None,
                                   type = int,
                                   metavar = 'Random seed',
                                   help = 'Set the random set for sampling')
    optional_sampling.add_argument('-n', '--sample-size',
                                   dest = 'sample_size',
                                   metavar = '<sample size>',
                                   type = int,
                                   default = _N,
                                   help = 'Sample size. Increase this value if suspected "garbage" reads obtained from sequencing (default: %(default)s)')
    optional_mapping = parser.add_argument_group('optional arguments for the alignment')
    optional_mapping.add_argument('--no-mapping',
                                  dest = 'nomap',
                                  action = "store_true",
                                  help = "Do not perform mappin with the aligner. This forces the number of iterations to one.")
    optional_mapping.add_argument('-a', '--aligner',
                                  dest = 'aligner',
                                  default = "bowtie2",
                                  help = "Excutable for the aligner bowtie2 (full path to the executable is needed is it cannot be found in the PATH). We may support other aligners in the future. (default: %(default)s)")
    optional_mapping.add_argument('--bowtie2-preset',
                                  dest = 'bowtie2_preset',
                                  metavar = '<preset string>',
                                  default = 'very-sensitive',
                                  choices = ['very-sensitive', 'sensitive', 'fast', 'very-fast'],
                                  help = 'Preset for bowtie2 (defaut: %(default)s, possible values {%(choices)s} - see the documentation of bowtie2 for details)')
    optional_mapping.add_argument('--bowtie2-threads',
                                  dest = 'bowtie2_threads',
                                  default = 1,
                                  type = int,
                                  help = 'Number of threads for bowtie2 (defaut: %(default)s)')
    parser.add_argument('--iter-max',
                        dest = 'itermax',
                        type = int,
                        default = 3,
                        help = 'Maximum number of iterations. Increase this number when working on metagenomics samples (default: %(default)s)')
    parser.add_argument('--pause',
                        dest = 'pause',
                        type = int,
                        default = 0,
                        help = 'Number of seconds to pause before exiting. (default: %(default)s)')
    parser.add_argument('--n-matches',
                          dest = 'nmatches',
                          type = int,
                          default = 5,
                          help = 'Maximum number of matches to retrieve (default: %(default)s)')
    parser.add_argument('-s', '--server',
                        dest = 'server',
                        default = "http://tapir.cbs.dtu.dk",
                        help = 'URL for the server (default: %(default)s). CAUTION: be gentle with our little server - hitting it too heavily may result in having your IP banned.')
    parser.add_argument('-p', '--port',
                        dest = 'port',
                        type = int,
                        default = 80,
                        help = 'Port on the server (default: %(default)s)')


    return parser


def sniff_samples(spl, timeout = 30):
    """ Query a dnasnout server (such as Tapir) and return
    the JSON data as a Python data structure. """
    q = {'sequences': list_asfasta(spl._l), 'refid_ignore': list()}
    req = urllib.request.Request(options.server + '/_sniff_paste',
                                 urllib.parse.urlencode(q).encode('ASCII'),
                                 HEADERS)

    con = urllib.request.urlopen(req, timeout=timeout)
    data = json.loads(con.read().decode('ASCII'))
    con.close()
    return data

def mapreads(m_i, m, unmapped_fn, out_d, server, aligner, 
             reference_dir = None,
             gz_tag='', bowtie2_preset = "--very-sensitive",
             bowtie2_threads = 1,
             screen=None, logger=None,
             bowtie2_inputformat = '-q'):
    """ Map reads """

    msg = 'match #{i}: fetching reference...'.format(i=m_i)
    _message(msg, logger, screen)

    refid = m['refid']

    if reference_dir is None:
        reference_dir = os.path.join(out_d, '..', 'references')
        # can raise FileNotFoundError or PermissionError
        os.mkdir(reference_dir)
        reference_dir = os.path.join(out_d, '..', 'references', 'refid_{0}'.format(refid))
    else:
        reference_dir = os.path.join(reference_dir, 'refid_{0}'.format(refid))

    # only create directory with reference information (bowtie2 index and so on...)
    # if not already there
    if not os.path.isdir(reference_dir):
        # can raise FileNotFoundError or PermissionError
        os.mkdir(reference_dir)

    # only download the reference if not already there
    reference_fa = os.path.join(reference_dir, 'ref.fa')
    if not os.path.isfile(reference_fa):
        try:
            con = urllib.request.urlopen(server + '/reference/{0}'.format(refid))
        except urllib.error.URLError as ue:
            if logger is not None:
                logger.info(str(ue)+"\n")
            return (reference_dir, None, None)
        except urllib.error.HTTPError as ue:
            if logger is not None:
                logger.info(str(ue)+"\n")
            return (reference_dir, None, None)            
        ref = json.loads(con.read().decode('ASCII'))
        if ref['seq'] == '':
            msg = 'Did not get the sequence from the server (presumably because too long).'
            _message(msg, logger, screen)
            return (reference_dir, None, None)
        seq_out = open(reference_fa, 'w')
        seq_out.write('>{0}:{1}'.format(refid, m['description'].lstrip('>'))); seq_out.write('\n')
        seq_out.write(ref['seq']); seq_out.write('\n')
        seq_out.flush();seq_out.close();


    matchref_dir = os.path.join(out_d, 'refid_{0}'.format(refid))
    # can raise errors
    os.mkdir(matchref_dir)

    # only build bowtie index if missing
    reference_idx = os.path.join(reference_dir, 'ref.1.bt2')
    if not os.path.isfile(reference_idx):
        msg = 'building bowtie index...'
        _message(msg, logger, screen)

        cmd = (os.path.join(os.path.dirname(aligner),
                            'bowtie2-build'), '--quiet',
               reference_fa, 
               reference_fa[:-3]) # clip the suffix '.fa'
        _message(' '.join(cmd), logger, None)

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            sys.stdout.write('error with bowtie.\n'); sys.stdout.flush()
            return (reference_dir, None, 0)

    msg = 'Aligning reads with bowtie2...'
    _message(msg, logger, screen)
    new_unmapped_fn = os.path.join(matchref_dir, 'un.fq')
    if gz_tag == '-gz':
        new_unmapped_fn += ".gz"
    cmd = (aligner, bowtie2_inputformat, bowtie2_preset, "-X", '2000',
           "-x", reference_fa[:-3], # clip the suffix '.fa'
           "-U", unmapped_fn,
           "-S", os.path.join(matchref_dir, 'ref.sam'),
           '--un'+gz_tag, new_unmapped_fn,
           '--threads', str(bowtie2_threads))
    if logger is not None:
            logger.info(' '.join(cmd))
    res = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    for row in res.split(b'\n'):
        row = row.decode('ASCII')
        if row.endswith('overall alignment rate'):
            percent = float(row[:row.index('%')])
    countaligned = percent
    #sys.stdout.write('\n{0}\n'.format(cmd)); sys.stdout.flush()
    msg = 'Complete'
    _message(msg, logger, screen)
    return reference_dir, new_unmapped_fn, countaligned

if __name__ == '__main__':
    import curses

    parser = _makeparser()
    options = parser.parse_args()

    if options.seed is not None:
        random.seed(seed)

    SCR_HEADER_ROW = 0
    SCR_ITERATION_ROW = 1
    SCR_DATA_ROW = 2
    SCR_HEADER_OFFSET = 4
    SCR_RES_ROW = 3
    SCR_MATCH_ROW = 0
    SCR_ITERATION_OFFSET = 2 # match "row" has 2 rows
    Result = namedtuple('Result', 'result error')

    import multiprocessing
    pool = multiprocessing.Pool(processes=options.n_processes)

    def do_file(unmapped_file, options, path_bowtie2, stdscr, logger=None):
        reference_dir = options.refdir

        count_threshold = 0
        entries = None
        try:
            entries = ngs_plumbing.parsing.open(unmapped_file.name)
        except ImportError as ie:
            return Result(None,
                          str(ie))            
        except ngs_plumbing.parsing.FileFormatError:
            return Result(None,
                          "File format error with %s" % unmapped_file.name)
        
        if unmapped_file.name.lower().endswith('.gz'):
            gz_tag = '-gz'
        else:
            gz_tag = ''

        inputfile_path = os.path.join(options.out_d, 
                                      os.path.splitext(os.path.basename(unmapped_file.name))[0])
        os.mkdir(inputfile_path)
        if logger is not None:
            logger.info('Created directory %s' % inputfile_path)

        Screen = namedtuple('Screen', 'stdscr x y')
        iteration = 0
        iterinfo = []
        prevp = 1
        notmapped = set()

        while os.stat(unmapped_file.name).st_size > 0 and iteration < options.itermax:
            if logger is not None:
                logger.info("Iteration %i" % iteration)
            iteration_offset = iteration*SCR_ITERATION_OFFSET + SCR_HEADER_OFFSET
            iteration += 1
            iteration_path = os.path.join(inputfile_path, 
                                          "iteration_%i" % iteration)
            os.mkdir(iteration_path)
            if entries is not None:
                entries = ngs_plumbing.parsing.open(unmapped_file.name)
            if unmapped_file.name.lower().endswith('.bam'):
                msg = "Converting BAM to FASTQ..."
                stdscr.addstr(SCR_DATA_ROW, 0, msg,
                              curses.A_NORMAL)
                stdscr.refresh()
                if logger is not None:
                    logger.info(msg)
                unmapped_fn = unmapped_file.name
                output_fn = unmapped_fn[:-3] + 'fq'
                sys.stdout.write(output_fn); sys.stdout.flush()
                output_file = open(output_fn, 'w')
                _tofastq_reads_bam(unmapped_file, output_file)
                unmapped_file.close()
                unmapped_fn = output_fn
                unmapped_file = open(unmapped_fn, 'rb')
            stdscr.addstr(SCR_ITERATION_ROW, 0,
                          'Iteration %i / %i' % (iteration, options.itermax),
                          curses.A_NORMAL)
            stdscr.refresh()
            entries = ngs_plumbing.parsing.open(unmapped_file.name)
            spl = ReservoirSample(options.sample_size)
            #candidate_entries = filter(None, entries)
            read_filter = _filter_passthrough(logger,
                                              Screen(stdscr, 0, SCR_DATA_ROW),
                                              '')
            logger.info(str(type(entries)))
            candidate_entries = read_filter(entries)
            for entry in candidate_entries:
                spl.add(entry)
            tmp = open(os.path.join(iteration_path, "spl.pkl"), "wb")
            pickle.dump(spl, tmp)
            tmp.close()
            msg = "Sending a request to %s..." % options.server
            stdscr.addstr(SCR_RES_ROW, 0, msg,
                          curses.A_NORMAL)
            stdscr.clrtoeol()
            stdscr.refresh()
            try:
                data = sniff_samples(spl)
            except urllib.error.URLError as ue:
                return Result(None, str(ue)+"\n")
            except http.client.BadStatusLine as bsl:
                return Result(None, str(bsl)+"\n")
            except socket.timeout as sto:
                return Result(None, 
                              'Connection with the server timed out.')
                
            f = open(os.path.join(iteration_path, "res.json"), "w")
            json.dump(data, f)
            f.close()
            unmapped_file.close()
            #unmapped_fn = None

            if options.nomap:
                msg = "No mapping performed. No need to iterate further."
                stdscr.addstr(SCR_RES_ROW, 0, msg,
                              curses.A_NORMAL)
                stdscr.clrtoeol()
                stdscr.refresh()
                return
            msg = "{0} matches (considering the first {1})".format(len(data['matches']), options.nmatches)
            stdscr.addstr(SCR_RES_ROW, 0, msg,
                          curses.A_NORMAL)
            stdscr.clrtoeol()
            stdscr.refresh()
            if logger is not None:
                logger.info(msg)
            best_countaligned = 0
            best_i = None
            res_list = []
            for m_i, m in enumerate(data['matches']):
                match_offset = m_i*2
                if m_i == options.nmatches:
                    break
                msg = m['description']
                try:
                    stdscr.addstr(iteration_offset+match_offset+1, 0, msg,
                                  curses.A_NORMAL)
                except curses.error:
                    pass
                stdscr.clrtoeol()
                try:
                    stdscr.addstr(iteration_offset+match_offset+2, 0, '',
                                  curses.A_NORMAL)
                except curses.error:
                    pass
                stdscr.clrtoeol()
                stdscr.refresh()
                if logger is not None:
                    logger.info(msg)
                try:
                    reference_dir, \
                        unmapped_fn, \
                        countaligned = mapreads(m_i, m, unmapped_file.name,
                                                iteration_path,
                                                options.server, options.aligner,
                                                reference_dir = reference_dir,
                                                gz_tag = gz_tag,
                                                bowtie2_preset = '--' + options.bowtie2_preset,
                                                screen = Screen(stdscr, 4, iteration_offset+match_offset+2),
                                                logger = logger)
                except Exception as e:
                    return Result(None, str(e)) 
                res_list.append((unmapped_fn, countaligned, m_i))

                if logger is not None:
                    logger.info('    %s %% of the reads\n' % str(countaligned))


                if countaligned is None:
                    try:
                        stdscr.addstr(iteration_offset+match_offset+2, 4, 'NA (alignment not performed)',
                                      curses.A_NORMAL)
                    except curses.error:
                        pass
                    notmapped.add(m['description'])
                else:
                    try:
                        stdscr.addstr(iteration_offset+match_offset+2, 4, '%f%%' % countaligned,
                                      curses.A_NORMAL)
                    except curses.error:
                        pass
                    if countaligned > best_countaligned:
                        best_i = m_i
                        best_countaligned = countaligned
                stdscr.clrtoeol()
                stdscr.refresh()

            if (best_i is None):
                msg = "No read matching."
                if logger is not None:
                    logger.info(msg)
                break
            else:                
                p = prevp * res_list[best_i][1]
                stdscr.addstr(iteration_offset+SCR_MATCH_ROW, 0, 
                              data['matches'][best_i]['description'],
                              curses.A_BOLD)
                stdscr.addstr(iteration_offset+SCR_MATCH_ROW+1, 0, 
                              '',
                              curses.A_BOLD)
                stdscr.clrtoeol()
                stdscr.addstr(iteration_offset+SCR_MATCH_ROW+1, 4, 
                              '%f%%' % p,
                              curses.A_BOLD)
                stdscr.clrtobot()
                stdscr.refresh()                
                if logger is not None:
                    logger.info('Best is: %s\n  with %f %% of the reads\n' % (data['matches'][best_i]['description'], p))
                unmapped_fn = res_list[best_i][0]
                iterinfo.append((res_list[best_i], data['matches'][best_i], p))
                prevp *= 1-(res_list[best_i][1]/100.0)
                # clearing the directories for the other mappings
                for i, elt in enumerate(res_list):
                    if i == best_i:
                        continue
                    tmp = 'refid_{0}'.format(data['matches'][i]['refid'])
                    try:
                        shutil.rmtree(os.path.join(iteration_path,
                                                   tmp))
                    except FileNotFoundError:
                        # if not there, don't remove it then...
                        pass
                res_list.append((unmapped_fn, countaligned, m_i))
                if logger is not None:
                    logger.info('Unmapped reads: %s' % unmapped_fn)
            unmapped_file = open(unmapped_fn, 'rb')
        import time
        time.sleep(options.pause)
        return Result((unmapped_file.name, iterinfo, notmapped), None)


    def runall(stdscr, options, pool, logger = None):
        stdscr.clear()

        stdscr.addstr(SCR_HEADER_ROW, 0,
                      'DNA-Snout v. %s' % __version__,
                      curses.A_REVERSE)
        stdscr.refresh()


        path_bowtie2 = shutil.which(options.aligner)
        if path_bowtie2 is None:
            return Result(None,
                          "Error: No executable bowtie2 could be found.")

        try:
            os.mkdir(options.out_d)
        except FileExistsError:
            return Result(None,
                          "Error: The output directory %s already exists." % options.out_d)        

        #prev_count = sys.maxsize
        res_allinputs = list()
        for unmapped_file in options.input_files:
            res_allinputs.append(do_file(unmapped_file, options, path_bowtie2, stdscr, logger=logger))
        return res_allinputs

    if (options.refdir is not None) and (not os.path.exists(options.refdir)):
        os.mkdir(options.refdir)
        
    if options.log_file is not None:
        options.log_file.close()
        logger = logging.getLogger("dnasnout_logger")
        logger.setLevel(logging.DEBUG)
        log_file = logging.FileHandler(options.log_file.name)
        log_file.setLevel(logging.DEBUG)
        logger.addHandler(log_file)
    else:
        logger = None
    res_allinputs = curses.wrapper(runall, options, pool, logger=logger)
    if type(res_allinputs) is Result and res_allinputs.error is not None:
        if logger is not None:
            logger.error(res_allinputs.error)
        goodbye(res_allinputs.error)

    for res in res_allinputs:
        if res.error is not None:
            if logger is not None:
                logger.error(res.error)
            print(res.error)
            continue
        print('Summary for %s' % os.path.basename(res[0][0]))
        import csv
        with open(os.path.join(options.out_d, "results.csv"), "w") as fh_out:
            csv_w = csv.writer(fh_out)
            csv_w.writerow(('Description', 'percentage'))
            if len(res[0][1]) == 0:
                print('No read matching.')
            else:
                for elt in res[0][1]:
                    print(elt[1]['description'])
                    print('    %f %%' % (elt[2]))
                    csv_w.writerow((elt[1]['description'], elt[2]))
            if len(res[0][2]) > 0:
                print('We suggest looking also at')
                for elt in res[0][2]:
                    print(elt)
