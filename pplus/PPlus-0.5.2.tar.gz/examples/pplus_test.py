#!/usr/bin/env python

import os
import urllib
import pplus

# Define a dependency
def count_word(line, word):
    return line.count(word)

# Define a distribute function
def count(pc, word): # PPlusConnection instance mandatory as first argument
    bigfile = pc.get_path('BIGFILE')

    counter = 0
    with open(bigfile) as f:
        for line in f:
            counter += count_word(line, word)

    return word, counter

def main():
    # PPlus Connection instantiation in debug mode
    pc = pplus.PPlusConnection(debug=True)
    print 'Starting experiment with id %s' % pc.id
    print 'Master session id %s' % pc.session_id

    # Download, if not exists, the input file
    if not os.path.exists('bigfile.txt'):
        file_url = 'http://bitbucket.org/slipguru/pplus/downloads/bigfile.txt'
        print "Downloading 'bigfile.txt'...",
        urllib.urlretrieve(file_url, 'bigfile.txt')
        print "done"

    # Put the file on the shared disk
    pc.put('BIGFILE', 'bigfile.txt')

    # Submit counting jobs
    words = ['love', 'strong', 'year', 'than', 'is', 'and'] # 6 jobs
    for w in words:
        pc.submit(count, (w,), depfuncs=(count_word,))

    # Collect (and print) the results
    results = pc.collect()
    print '\n%d tasks on %d returned' % (len(results), len(words))
    for w, c in results:
        print "Found '%s' %d times" % (w, c)

if __name__ == '__main__':
    main()

# Results on bigfile.txt
#6 tasks on 6 returned
#Found 'love' 2763 times
#Found 'strong' 499 times
#Found 'year' 1313 times
#Found 'than' 2493 times
#Found 'is' 81588 times
#Found 'and' 87585 times
