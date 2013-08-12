"""
Generate a passphrase consisting of words chosen from word list dictionaries.
"""

import math
import random
import argparse
import logging

bits_default = 164
parser = argparse.ArgumentParser(description=__doc__.strip())
parser.add_argument(
    'wordlist', nargs='*', default = ['/usr/share/dict/words'],
    help='one or more word list dictionaries with one word per line '
    '(default: %(default)r)')
parser.add_argument(
    '-d', '--delimiter', default=' ',
    help='delimiter that separates the words in the passphrase '
    '(default: %(default)r)')
group = parser.add_mutually_exclusive_group()
group.add_argument(
    '-b', '--bits', type=float,
    help='minimum bits of entropy, determines the number of words '
    '(default: %s)' % bits_default)
group.add_argument(
    '-l', '--length', type=int,
    help='length of the passphrase in number of words')

logger = logging.getLogger('passphrasegen')


def generate(wordlists,
             bits=None, length=parser.get_default('length')):
    if bits and length:
        raise ValueError("Specify only one of 'bits' and 'length' arguments")

    words = set()
    for wordlist in wordlists:
        words.update(
            word.strip().replace("'", "").lower() for word in open(wordlist))
    words = list(words)
    words_bits = math.log(len(words), 2)
    logger.info('The word lists have %s words with %s bits of entropy',
                len(words), round(words_bits, 1))

    if length:
        length = length
    else:
        if bits is None:
            bits = bits_default
        length = int(math.ceil(bits / words_bits))
    passphrase_bits = length * words_bits
    logger.info('The passphrase has %s words with %s bits of entropy',
                length, round(passphrase_bits, 1))

    return [random.choice(words) for n in xrange(length)]
    

def main(args=None, namespace=None):
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args(args, namespace)
    print args.delimiter.join(generate(
        args.wordlist, args.bits, args.length))

if __name__ == '__main__':
    print main()
