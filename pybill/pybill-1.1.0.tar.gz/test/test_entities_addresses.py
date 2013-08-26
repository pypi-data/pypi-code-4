# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib.entities.addresses import PersonAddress, OrganisationAddress


class PersonAddressTest(TestCase):
    def setUp(self):
        """
        Called before each test of this class.
        """
        self.addr = PersonAddress()
        self.addr.honorific  =   u" Mr               "
        self.addr.firstname  =   u" Robert           "
        self.addr.other_name =   u" T.               "
        self.addr.surname    =   u" Smith            "
        self.addr.lineage    =   u" Jr               "
        self.addr.streets    = [ u"                  ",
                                 u" Main street, 1st ",
                                 u" Yellow House     " ]
        self.addr.post_box   =   u" Post box    # 3  "
        self.addr.city       =   u" LONDON           "
        self.addr.post_code  =   u" 65789            "
        self.addr.state      =   u" (London County)  "
        self.addr.country    =   u" UNITED KINGDOM   "
        
    def test_get_postal_address_lines(self):
        """
        Test the method giving the lines of the postal address.
        """
        addr_lines = self.addr.get_postal_address_lines()
        expected_lines = [ u"Main street, 1st",
                           u"Yellow House",
                           u"Post box # 3",
                           u"65789 LONDON (London County)",
                           u"UNITED KINGDOM" ]
        self.assertEqual(addr_lines, expected_lines)

    def test_get_person_name(self) :
        name = self.addr.get_person_name()
        expected_name = u"Mr Robert T. Smith Jr"
        self.assertEqual(name, expected_name)


class OrganisationAddressTest(TestCase):
    def setUp(self):
        """
        Called before each test of this class.
        """
        self.addr = OrganisationAddress()
        self.addr.name       =   u" Stuff Corporation "
        self.addr.streets    = [ u"                   ",
                                 u" Main street, 1st  ",
                                 u" Yellow House      " ]
        self.addr.post_box   =   u" Post box    # 3   "
        self.addr.city       =   u" LONDON            "
        self.addr.post_code  =   u" 65789             "
        self.addr.state      =   u" (London County)   "
        self.addr.country    =   u" UNITED KINGDOM    "
        
    def test_get_postal_address_lines(self):
        """
        Test the method giving the lines of the postal address
        """
        addr_lines = self.addr.get_postal_address_lines()
        expected_lines = [ u"Main street, 1st",
                           u"Yellow House",
                           u"Post box # 3",
                           u"65789 LONDON (London County)",
                           u"UNITED KINGDOM" ]
        self.assertEqual(addr_lines, expected_lines)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
