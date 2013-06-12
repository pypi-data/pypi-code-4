'''
Simple access to the reference genomes at UCSC.
Main class.

Copyright 2013, Konstantin Tretyakov.
http://kt.era.ee/

Licensed under MIT license.
'''

import urllib, os.path
from twobitreader import TwoBitFile

class GenomeException(Exception):
    pass
class HttpException(Exception):
    pass
class ErrorAwareURLOpener(urllib.FancyURLopener):
  def http_error_default(self, url, fp, errcode, errmsg, headers):
    raise HttpException("404")
_urlopener = ErrorAwareURLOpener()

class Genome(TwoBitFile):
    def __init__(self, genome_id, cache_dir=os.path.expanduser("~/.ucscgenome"), use_web=True, reporthook=None, 
                 source_url_pattern="http://hgdownload.cse.ucsc.edu/goldenPath/%(id)s/bigZips/%(id)s.2bit"):
        '''
        Genome can be initialized in multiple ways
        
         * By providing a filename as a single argument: Genome('hg19.2bit')
           The file must be in the "twobit" format (http://www.its.caltech.edu/~alok/reviews/blatSpecs.html)
         * By providing the name of the UCSC genome, e.g. Genome('hg19').
           In this case, Genome will "intelligently" search for the corresponding genome's 2bit file.
           The file will be searched in current directory, cache directory, or downloaded from the web to the cache, if possible.
           
        Other arguments are the following:
         
         * cache_dir - specifies the cache directory where to look for twobit files. Also, if file is not found, it will be downloaded there.
         * use_web - specifies whether it is allowed to use the web to download stuff and write to cache.
         * reporthook - the reporthook provided to urlopen for tracking download progress. Must be a function (block_count, block_size, total_bytes), see urlretrieve documentation.
         * source_url_pattern - the way of constructing an URL from the given genome id. The '%(id)s' within the pattern will be replaced with the ID. 
         
        Note that not all genomes are available at UCSC in 2bit format (e.g. sacCer1 is not).
        '''
        self.genome_file = open_genome_file(genome_id, cache_dir=cache_dir, use_web=use_web, reporthook=reporthook, source_url_pattern=source_url_pattern)            
        super(Genome, self).__init__(self.genome_file.name)
        
    def close(self):
        '''
        Closes the opened file object.
        '''
        self.genome_file.close()

def open_genome_file(genome_id, cache_dir=os.path.expanduser("~/.pyliftover"), use_web=True, reporthook=None, 
                     source_url_pattern="http://hgdownload.cse.ucsc.edu/goldenPath/%(id)s/bigZips/%(id)s.2bit", ):
    '''
    A "smart" way of obtaining 2bit genome files.
    By default acts as follows:
     1. If the file ``<genome_id>`` exists, opens it via open(..., 'rb')
     2. Otherwise, if the file ``<genome_id>.2bit`` exists, opens it.
     3. Otherwise, checks whether ``<cache_dir>/<genome_id>.2bit`` exists.
        This and the following steps may be disabled by specifying cache_dir = None.
     4. If file still not found attempts to download the file from the URL
        <source_url_pattern % {'id': <genome_id>} to the cache and open from there.
        This step may be disabled by specifying use_web=False.
        
    In case of errors (e.g. URL cannot be opened or downloaded), an exception is thrown.
    '''
    if os.path.isfile(genome_id):
        return open(genome_id, 'rb')
    if os.path.isfile('%s.2bit' % genome_id):
        return open('%s.2bit' % genome_id, 'rb')
    if cache_dir is not None:
        target_file = os.path.join(cache_dir, '%s.2bit' % genome_id)
        if os.path.isfile(target_file):
            return open(target_file, 'rb')
        elif use_web:
            # Download from web to cache
            source_url = source_url_pattern % {'id': genome_id}
            try:
                try:
                    if not os.path.isdir(cache_dir):
                        os.mkdir(cache_dir)
                    (downloaded_filename, headers) = _urlopener.retrieve(source_url, target_file, reporthook=reporthook)
                except HttpException,e:
                    raise GenomeException("Failed to download %s to %s" % (source_url, target_file))
            except:
                # If the download failed halfway we'll have a partial file in the cache.
                # Drop it.
                if os.path.isfile(target_file):
                    os.unlink(target_file)
                raise
            # Now open
            return open(target_file, 'rb')
        else:
            raise GenomeException("Genome %s not present in cache and web access disabled" % genome_id)
    else:
        raise GenomeException("Genome %s not found" % genome_id)
