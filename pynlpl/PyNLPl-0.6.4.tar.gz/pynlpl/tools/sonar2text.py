#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os

if __name__ == "__main__":
    sys.path.append(sys.path[0] + '/../..')
    os.environ['PYTHONPATH'] = sys.path[0] + '/../..'

from pynlpl.formats.sonar import CorpusFiles, Corpus
from pynlpl.statistics import FrequencyList

sonardir = sys.argv[1]


for i, doc in enumerate(Corpus(sonardir)):
    print >>sys.stderr, "#" + str(i) + " Processing " + doc.filename
    print
    words = [ w for w, _,_,_ in doc]
    out =  " ".join(words)
    print out.encode('utf-8')
      
freqlist.save('sonarfreqlist.txt')
lemmapos_freqlist.save('sonarlemmaposfreqlist.txt')
poshead_freqlist.save('sonarposheadfreqlist.txt')
pos_freqlist.save('sonarposfreqlist.txt')
            
print unicode(freqlist).encode('utf-8')
