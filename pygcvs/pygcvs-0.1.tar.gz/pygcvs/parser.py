from __future__ import unicode_literals, print_function

import csv
import logging

logger = logging.getLogger(__name__)


class GcvsParser(object):
    """
    A parser for GCVS data format.

    Example usage:

        >>> with open('iii.dat', 'rb') as fp:
        ...     parser = GcvsParser(fp)
        ...     for star in parser:
        ...         print(star['name'])
        R AND
        S AND
        #...
        V0515 VUL
        V0516 VUL
    """

    def __init__(self, fp):
        """
        Creates the parser and feeds it a file-like object.

        :param fp: a file-like object or a generator yielding strings
        """
        self.reader = csv.reader(fp, delimiter=str('|'))
        # skip two initial lines
        next(self.reader)
        next(self.reader)

    def __iter__(self):
        for row in self.reader:
            if len(row) != 15:
                continue
            try:
                yield self.row_to_dict(row)
            except Exception:
                logger.exception("Error in row: %s", row)
                continue

    def row_to_dict(self, row):
        """
        Converts a raw GCVS record to a dictionary of star data.
        """
        name = self.parse_name(row[1])
        ra, dec = self.parse_coordinates(row[2])
        variable_type = row[3].strip()
        max_magnitude, symbol = self.parse_magnitude(row[4])
        min_magnitude, symbol = self.parse_magnitude(row[5])
        if symbol == '(' and max_magnitude is not None:
            # this is actually amplitude
            min_magnitude = max_magnitude + min_magnitude
        epoch = self.parse_epoch(row[8])
        period = self.parse_period(row[10])
        return {
            'name': name,
            'ra': ra,
            'dec': dec,
            'variable_type': variable_type,
            'max_magnitude': max_magnitude,
            'min_magnitude': min_magnitude,
            'epoch': epoch,
            'period': period,
        }

    def parse_name(self, name_str):
        """
        Normalizes variable star designation (name).
        """
        name = name_str[:9]
        return ' '.join(name.split()).upper()

    def parse_coordinates(self, coords_str):
        """
        Returns a pair of PyEphem-compatible coordinate strings (Ra, Dec).
        """
        ra = '%s:%s:%s' % (coords_str[0:2], coords_str[2:4], coords_str[4:8])
        dec = '%s:%s:%s' % (coords_str[8:11], coords_str[11:13], coords_str[13:15])
        return (ra, dec)

    def parse_magnitude(self, magnitude_str):
        """
        Converts magnitude field to a float value, or ``None`` if GCVS does
        not list the magnitude.

        Returns a tuple (magnitude, symbol), where symbol can be either an
        empty string or a single character - one of '<', '>', '('.
        """
        symbol = magnitude_str[0].strip()
        magnitude = magnitude_str[1:6].strip()
        return float(magnitude) if magnitude else None, symbol

    def parse_epoch(self, epoch_str):
        """
        Converts epoch field to a float value (adding 24... prefix), or
        ``None`` if there is no epoch in GCVS record.
        """
        epoch = epoch_str[:10].strip()
        return 2400000.0 + float(epoch) if epoch else None

    def parse_period(self, period_str):
        """
        Converts period field to a float value or ``None`` if there is
        no period in GCVS record.
        """
        period = period_str[1:17].strip()
        return float(period) if period else None
