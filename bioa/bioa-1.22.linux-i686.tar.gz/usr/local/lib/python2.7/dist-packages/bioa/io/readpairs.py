# -*- coding: utf-8 -*-
"""
==========================================
IO based functions for handling read pairs
==========================================
"""

__all__ = ["parse_pairs",
           "get_pairs_from_file",
           "write_pairs",
           "write_pairs_to_file"]

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.


def parse_pairs(stream, delimiter=","):
    """ Parses a stream of read-sequence frequency pairs into a dict.

    Parameters
    ----------
    stream : iterable object
        An iterable object which to pull the pairs from.

    delimiter : str (optional, default=",")
        The character which to delimit pairs by.

    Returns
    -------
    pair_table : dict
        Lookup table of read-sequences and their respective frequency.
    """
    if not stream:
        raise ValueError("Valid stream required!")

    pairs = {}
    for line in stream:
        pair = line.split(delimiter)
        ref, freq = pair[0], float(pair[1])
        pairs[ref] = freq
    return pairs


def get_pairs_from_file(filename, delimiter=","):
    """ Opens and parses a file into read-sequence frequency pairs.

    Parameters
    ----------
    filename : str
        Path to the file containing the pairs.

    delimiter : str (optional, default=",")
        The character which to delimit pairs by within the file.

    Returns
    -------
    pair_table : dict
        Lookup table of read-sequences and their respective frequency.
    """
    if not filename:
        raise ValueError("Non-empty file path required!")

    pairs = {}
    with open(filename, "r") as pair_file:
        pairs = parse_pairs(pair_file, delimiter)
    return pairs


def write_pairs(read_pairs, stream, delimiter=","):
    """ Writes the read-freq pairs out to the stream.

    Parameters
    ----------
    read_pairs : dict
        Lookup table of read-sequences and their respective frequency.

    stream : writeable stream
        A stream to write the pairs out to.

    delimiter = str (optional, default=",")
        The character which to delimit pairs by within the file.

    Returns
    -------
    None
    """
    if not read_pairs:
        raise ValueError("Non-empty read-pairs required!")
    if not stream:
        raise ValueError("Valid stream required!")

    for read, freq in read_pairs.items():
        stream.write(read + delimiter + str(freq) + "\n")


def write_pairs_to_file(read_pairs, filename, delimiter=","):
    """ Writes the read-freq pairs out to the specified file.

    Parameters
    ----------
    read_pairs : dict
        Lookup table of read-sequences and their respective frequency.

    filename : str
        Path to the file containing the pairs.

    delimiter = str (optional, default=",")
        The character which to delimit pairs by within the file.

    Returns
    -------
    None
    """
    if not read_pairs:
        raise ValueError("Non-empty read-pairs required!")
    if not filename:
        raise ValueError("Non-empty file path required!")

    with open(filename, "w") as pair_file:
        write_pairs(read_pairs, pair_file, delimiter)
