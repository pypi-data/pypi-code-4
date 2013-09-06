import os.path
from pandas import DataFrame
import numpy as np
import unittest
import re
import glob
import sys
from nomad import fetch_nomad_box, _determine_usnob1_id_from_usnob1_integer


class Error(Exception):
    pass


class Test_nomad(unittest.TestCase):

    def setUp(self):
        None

    def read_test_data_file(self, filename):
        """
        Read in data from a file (full path and name given in filename input) containing example
        retrievals of NOMAD stars from:
            http://www.nofs.navy.mil/data/fchpix/

        return is a tuple containing:
            dict of search parameters
            pandas DataFrame of stars
        """
        if not os.path.isfile(filename):
            raise Error("Test data file does not exist or problem with file: " + filename)
        txt = open(filename, 'r').readlines()
        search_params = {}
        for curlinenum, curline in enumerate(txt):
            if curline.startswith('#END'):   # end of search parameters
                break
            search_params[curline.split('=')[0].replace('#', '').strip()] = {
                'value': curline.split('=')[1].split('/', 1)[0].strip(),
                'comment': curline.split('/', 1)[1].strip()}
        while not txt[curlinenum].startswith('#1'):
            curlinenum += 1
        hdrline1 = txt[curlinenum]
        while not txt[curlinenum].startswith('#2'):
            curlinenum += 1
        hdrline2 = txt[curlinenum]
        headers1 = [a.strip() for a in hdrline1[2:].split('|')]
        headers2 = [a.strip() for a in hdrline2[2:].split('|')]
        headers = [headers1[i] + ' ' + headers2[i] for i in range(len(headers1))][:-1]
        headers = [a.replace(' mag', 'mag') for a in headers]
        split_at = [a.start() for a in re.finditer('\|', hdrline1)][:-1]
        split_row = lambda row: [row[i:j].replace('\n', '') for i, j in zip([0] + split_at, split_at + [None])]
        data = [split_row(row) for row in txt[curlinenum + 2:]]
        df = DataFrame(data, columns=headers)
        df.index = df['id id'].apply(lambda x: x.strip())
        df.index.name = 'NOMAD id'
        columns_to_drop = ['id id']
        df['RAJ2000'] = (df['RA hh mm ss'].apply(lambda x: float(x.split()[0])) +
                         df['RA hh mm ss'].apply(lambda x: float(x.split()[1])) / 60. +
                         df['RA hh mm ss'].apply(lambda x: float(x.split()[2])) / 3600.) * 15.
        columns_to_drop.append('RA hh mm ss')
        dec_sign = lambda x: -1.0 if x.strip()[0] == '-' else 1.0
        df['DEJ2000'] = (df['DEC dd mm ss'].apply(dec_sign) *
                         (df['DEC dd mm ss'].apply(lambda x: float(x.split()[0].replace('+', '').replace('-', ''))) +
                          df['DEC dd mm ss'].apply(lambda x: float(x.split()[1])) / 60. +
                          df['DEC dd mm ss'].apply(lambda x: float(x.split()[2])) / 3600.))
        columns_to_drop.append('DEC dd mm ss')
        columns_to_drop.append('ExtractID id')
        df = df.drop(columns_to_drop, axis=1)
        for column in df:   # check first in each column for ability to convert to integer, then float, then leave alone
            if df[column].dtype == object and column != 'Flags hex':
                if df[column][0].strip().lstrip('-').lstrip('+').isdigit():
                    df[column] = df[column].apply(np.int)
                elif df[column][0].strip().lstrip('-').lstrip('+').replace('.', '0').isdigit():
                    df[column] = df[column].apply(np.float)
        return search_params, df

    def radec_range_from_search_parameters(self, search_params):
        RAJ2000 = (float(search_params['RA']['value'].split()[0]) +
                   float(search_params['RA']['value'].split()[1]) / 60. +
                   float(search_params['RA']['value'].split()[2]) / 3600.) * 15.
        dec_sign = lambda x: -1.0 if x.strip()[0] == '-' else 1.0
        DEJ2000 = (dec_sign(search_params['DEC']['value']) *
                   (float(search_params['DEC']['value'].split()[0].replace('+', '').replace('-', '')) +
                    float(search_params['DEC']['value'].split()[1]) / 60. +
                    float(search_params['DEC']['value'].split()[2]) / 3600.))
        ra_halfwidth = (float(search_params['DRA']['value']) / 2.0) / np.cos(np.radians(DEJ2000))
        ra_range = [(RAJ2000 - ra_halfwidth) % 360.0, (RAJ2000 + ra_halfwidth) % 360.0]
        # TODO: figure out if need to do cos(dec) at both top and bottom of range?
        dec_halfwidth = float(search_params['DDEC']['value']) / 2.0
        dec_range = [DEJ2000 - dec_halfwidth, DEJ2000 + dec_halfwidth]
        return ra_range, dec_range

    def decrease_radec_range(self, ra_range, dec_range):
        dec_decrease_by_degrees = (max(dec_range) - min(dec_range)) * 0.20   # 10 % on each edge
        new_dec_range = [dec_range[0] + dec_decrease_by_degrees, dec_range[1] - dec_decrease_by_degrees]
        if ra_range[1] > ra_range[0]:
            ra_decrease_by_degrees = (max(ra_range) - min(ra_range)) * 0.20   # 10 % on each edge
        else:
            ra_decrease_by_degrees = ((360.0 - ra_range[0]) + ra_range[1]) * 0.20   # 10 % on each edge
        new_ra_range = [(ra_range[0] + ra_decrease_by_degrees) % 360.0,
                        (ra_range[1] - ra_decrease_by_degrees) % 360.0]
        return new_ra_range, new_dec_range

    def filter_starlist_by_radec_range(self, stars, ra_range, dec_range):
        stars = stars[(stars['DEJ2000'] >= dec_range[0]) & (stars['DEJ2000'] <= dec_range[1])]
        if ra_range[1] > ra_range[0]:
            stars = stars[(stars['RAJ2000'] >= ra_range[0]) & (stars['RAJ2000'] <= ra_range[1])]
        else:
            stars = stars[(stars['RAJ2000'] >= ra_range[0]) | (stars['RAJ2000'] <= ra_range[1])]
        return stars

    def retrieve_nomad_from_search_parameters(self, search_params):
        """
        Use the fetch_nomad_box routine to fetch NOMAD stars for the same search area and epoch
        as specified in search_params, which would have been read in from a example test data file
        retrieved from the NOMAD web site
        """
        ra_range, dec_range = self.radec_range_from_search_parameters(search_params)
        print "Retrieving on ranges:"
        print "      RA = " + str(ra_range)
        print "     DEC = " + str(dec_range)
        return fetch_nomad_box(ra_range, dec_range, epoch=float(search_params['EPOCH']['value']))

    def get_list_of_test_data_files(self):
        # TODO: need to generalize to finding where nomad was installed and looking there
        return glob.glob('/Users/hroe/py/nomad/test_data/nomad*txt')

    def starlists_contain_same_NOMAD_ids(self, stars1, stars2):
        return set(stars2.index) == set(stars1.index)

    def assert_starlist_parameters_almost_equal_by_decimal_places(self, stars1, stars2, param_name, decimal_places):
        # assume that starlists_contain_same_NOMAD_ids already tested
        for curstar in stars1.index:
            self.assertAlmostEqual(stars1.ix[curstar][param_name], stars2.ix[curstar][param_name], decimal_places)

    def assert_starlist_parameters_almost_equal_by_delta(self, stars1, stars2, param_name, delta):
        # assume that starlists_contain_same_NOMAD_ids already tested
        for curstar in stars1.index:
            self.assertAlmostEqual(stars1.ix[curstar][param_name], stars2.ix[curstar][param_name], delta=delta)

    def test_determine_usnob1_id_from_usnob1_integer(self):
        usnob1_integer = 701776574
        self.assertTrue(_determine_usnob1_id_from_usnob1_integer(usnob1_integer) == '1000-0183105')

    def test_check_all_test_data_files(self):
        datafiles = self.get_list_of_test_data_files()
        for cur_filename in datafiles:
            search_params, stars_original = self.read_test_data_file(cur_filename)
            # NOTE: we've seen some small inconsistencies at the edges of search fields, e.g. in the test
            #       fields retrieved from http://www.nofs.navy.mil/data/fchpix/   there have been
            #       stars returned that are just outside the RA/DEC boundaries.
            #       Probably just rounding errors, but avoid those (literally) edge cases, we will compare
            #       only the inner +-90% of the retrieved fields.
            full_ra_range, full_dec_range = self.radec_range_from_search_parameters(search_params)
            ra_range, dec_range = self.decrease_radec_range(full_ra_range, full_dec_range)
            stars_original = self.filter_starlist_by_radec_range(stars_original, ra_range, dec_range)
            print "starting test_check_all_test_data_files on: " + cur_filename
            print "       RA:  " + str(search_params['RA']['value']) + ' width = ' + str(search_params['DRA']['value'])
            print "      DEC: " + str(search_params['DEC']['value']) + ' width = ' + str(search_params['DDEC']['value'])
            print "    epoch: " + str(search_params['EPOCH']['value'])
            print "   Nstars: " + str(len(stars_original))
            stars = self.retrieve_nomad_from_search_parameters(search_params)
            stars = self.filter_starlist_by_radec_range(stars, ra_range, dec_range)
            self.assertTrue(self.starlists_contain_same_NOMAD_ids(stars_original, stars))
            for cur_band in ['Bmag', 'Vmag', 'Rmag', 'Jmag', 'Hmag', 'Kmag']:
                self.assert_starlist_parameters_almost_equal_by_decimal_places(stars_original, stars, cur_band, 3)
            # We require DEC coordinates to match within 1 milliarcsec (actually do just under 1 mas)
            self.assert_starlist_parameters_almost_equal_by_delta(stars_original, stars, 'DEJ2000', 0.000999 / 3600.)
            # Similarly we require RA coordinates to match within 1 mas (but, note tolerance adjusted for cos(dec))
            cosdec = np.cos(np.radians(stars['DEJ2000'].mean()))
            self.assert_starlist_parameters_almost_equal_by_delta(stars_original, stars, 'RAJ2000',
                                                                  0.000999 / (3600. * cosdec))

    def test_check_edges_of_retrieved_fields(self):
        """
        check that stars aren't being missed at the edges of requested fields, by retrieving over a much
        wider area and then trimming, compared with retrieving only over a the narrower trimmed area.
        """
        # pick an RA range where we've predetermined there's a star right at the edge
        # 0064 15.25 15.25 15.4999305556
        ra_range = [15.25 * 15.0, 16.0 * 15.0]
        dec_range = [-85., -83.]
        stars = fetch_nomad_box(ra_range, dec_range, epoch=2000.0)
        stars_largebox = fetch_nomad_box([ra_range[0] - 1.0, ra_range[1] + 1.0],
                                         [dec_range[0] - 1.0, dec_range[1] + 1.0], epoch=2000.0)
        stars_largebox_filtered = self.filter_starlist_by_radec_range(stars_largebox, ra_range, dec_range)
        self.assertTrue(self.starlists_contain_same_NOMAD_ids(stars_largebox_filtered, stars))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        unittest.main()
