'''
Simple access to the reference genomes at UCSC.
The library acts as a thin wrapper around the "twobitreader" library, providing
easy "caching" functionality.

Copyright 2013, Konstantin Tretyakov.
http://kt.era.ee/

Licensed under MIT license.

The primary usage example is the following::

   from ucscgenome import Genome
   g = Genome('sacCer2')
   print str(g['chrI'][0:100])

On the second line of the above example the following steps are performed:

* The local ``cache directory`` is searched for the pre-downloaded genome data. If the data is readily available, it is opened for reading.
* If there is not cached version of the ``sacCer2`` genome, it is downloaded from the UCSC site to the cache directory.
* The local data is downloaded and stored using the compact `2bit <http://www.its.caltech.edu/~alok/reviews/blatSpecs.html>`_ format.

You can configure the details of the procedure by providing additional options to the ``Genome`` constructor::

   g = Genome('hg19', cache_dir='my_genomes', use_web=False)
   
which means that the genome data is to be searched for in the ``./my_genomes`` directory and in no case should a download be attempted, or::

   g = Genome('hg19', source_url_pattern='http://my.site.com/genomes/%(id)s/%(id)s.2bit')

which means that the genomic data is to be downloaded from your own server rather than UCSD's.
'''

from genome import Genome