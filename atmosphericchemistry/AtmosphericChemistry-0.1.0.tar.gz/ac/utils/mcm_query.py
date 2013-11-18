# -*- coding: utf-8 -*-
"""
MCM_Query

Python wrapper for querying species information from the
Leeds Master Chemical Mechanism (MCM)
"""


import urllib2
import lxml.html as lh

MCM_url = "http://mcm.leeds.ac.uk/MCM/"

class Compound(object):
    """ A class for retrieving record details about a compound by CSID.

    The purpose of this class is to provide access to various parts of the
    ChemSpider API that return information about a compound given its CSID.
    Information is loaded lazily when requested, and cached for future access.
    """
 
    def __init__(self, name):
        """ Initialize with a name as str """
        if isinstance(name, basestring):
            self._name = name
        else:
            raise TypeError('Compound must be initialised with a name as str')

        self._molecularweight = None
        self._smiles = None
        self._inchi = None
        self._synonyms = None

        # Return exception if it is occured in opening the web page or parsing its values 
        try:
            self.compoundInfo()
        except Exception as e:
            print e
        


    def __repr__(self):
        return "Compound(%s)" % self._name

    @property
    def molecular_weight(self):
        """ Retrieve molecular weight from ChemSpider """
        return self._molecularweight  

    @property
    def canonical_smiles(self):
        """ Retrieve SMILES string from ChemSpider """
        return self._smiles

    @property
    def inchi(self):
        """ Retrieve InChi string from ChemSpider """
        return self._inchi

    @property
    def synonyms(self):
        """ Retrieve monoisotropic mass from ChemSpider """
        return self._synonyms

    
    def compoundInfo(self):
        """ Retrive the web page for given compound id and parse it. """
        #construct search URL for given compound name
        searchurl = '%s/browse.htt?species=%s' % (MCM_url, self._name)

        #get html response
        try:
            response = urllib2.urlopen(searchurl, timeout = 10)
        except urllib2.URLError as err:
            raise err

        # get root of document
        root = lh.parse(response).getroot()
        #find table containing result using CSS selector
        table = root.cssselect('table.infobox')
        #rows containing all result fields
        rows = table[0].findall("tr")

        #iterate
        for row in rows:
            #heading or title as first column
            title = row.getchildren()[0].text
            #store values here
            values = list()
            #we have span elements under second column  
            for element in row.getchildren()[1].getchildren():
                #throws exception object if record not found
                if("Exception" in element.text):
                    raise Exception('Exception occured in finding values')
                else:
                    values.append(element.text.strip(' \n\t;'))
            # assign values
            if title == 'Molecular weight':
                self._molecularweight = values
            elif title == 'SMILES':
                self._smiles = values
            elif title == 'Inchi':
                self._inchi = values
            elif title == 'Synonyms': 
                self._synonyms = values       
    
    def get_properties(self):
        """ Returns complete compound information """
        return {'molecularweight':self.molecular_weight, 
                'smiles':self.canonical_smiles, 
                'inchi':self.inchi, 
                'synonyms':self.synonyms
               }

def get_compound(name):
    """ Returns Compound object """
    try:
        obj = Compound(name)
        return obj
    except:
        return None

def test_mcm_query(name="CH3CHO"):
    test = get_compound(name)
    print "test: ", test.get_properties()


