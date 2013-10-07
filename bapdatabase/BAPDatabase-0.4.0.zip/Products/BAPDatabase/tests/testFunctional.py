from unittest import TestSuite, makeSuite
from BeautifulSoup import BeautifulSoup
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class BAPFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for BAP object """
    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.BAPDatabase.BAPDatabase import manage_add_bap
        addNyFolder(self.portal, 'countries', contributor='admin', submitted=1)
        #add a country
        addNyFolder(self.portal.countries, id='austria', title='Austria', contributor='admin', submitted=1)
        addNyFolder(self.portal.countries, id='france', title='France', contributor='admin', submitted=1)
        manage_add_bap(self.portal, 
                    id = 'bap', 
                    db_host = 'localhost', 
                    db_port = '3306',
                    db_username = 'bap',
                    db_password = 'bap',
                    db_name='bap')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['bap'])
        import transaction; transaction.commit()

    def test_connection(self):
        objectives = self.portal.bap.get_objectives()
        self.assertEqual(len(objectives), 15)

    def test_objectives(self):
        self.browser.go('http://localhost/portal/countries/austria/bap')
        html = self.browser.get_html()
        self.failUnless("Objective1" in html)
    
    def test_actions(self):
        self.browser.go('http://localhost/portal/countries/austria/bap')
        html = self.browser.get_html()
        self.failUnless("Target" in html)    

    def test_A1_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A1_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Additional detail & Narrative summary of the information'))

    def test_A1_1_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A1_1_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'How complete is the Natura 2000 network?')
        
        record = self.portal.bap.get_report('A1_1_1_Natura2000Compleat', country='Austria')
        self.assertTrue(hasattr(record, 'HabitatSites'))

        record = self.portal.bap.get_report('A1_1_1_Natura2000Plan', country='Austria')
        self.assertTrue(hasattr(record, 'Compleat'))

    def test_A1_1_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A1_1_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Additional detail & Narrative summary of the above information'))

    def test_A1_1_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A1_1_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Indicate the number of complaints/infringements (legal cases)')

        record = self.portal.bap.get_report('A1_1_3', country='Austria')
        self.assertTrue(hasattr(record, 'Y2004'))

    def test_A1_2_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A1_2_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Are tools in place or developed to support ecological connectivity?')

        record = self.portal.bap.get_report('A1_2_3', country='Austria')
        self.assertTrue(hasattr(record, 'ToolInPlace'))

    def test_A1_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A1_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('What is the conservation status of birds'))

        record = self.portal.bap.get_report('A1_3', country='Austria')
        self.assertTrue(hasattr(record, 'BirdGrn'))

    def test_A1_3_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A1_3_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Indicate the number of action plans per species group')

        record = self.portal.bap.get_report('A1_3_1_ActionPlan', country='Austria')
        self.assertTrue(hasattr(record, 'BirdComp'))

        record = self.portal.bap.get_report('A1_3_1_BirdIndicator', country='Austria')
        self.assertTrue(hasattr(record, 'IndicatorDev'))

        record = self.portal.bap.get_report('A1_3_1_RedList', country='Austria')
        self.assertTrue(hasattr(record, 'Bird'))

        record = self.portal.bap.get_report('A1_3_1_BirdMonitoring', country='Austria')
        self.assertTrue(hasattr(record, 'active'))

    def test_A2_1_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'EAFRD')

        record = self.portal.bap.get_report('A2_1_1', country='Austria')
        self.assertTrue(hasattr(record, 'EAFRDTotal'))

    def test_A2_1_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Share of high nature value (HNV) farmland areas.')

        record = self.portal.bap.get_report('A2_1_3_HNV', country='Austria')
        self.assertTrue(hasattr(record, 'Area'))

        record = self.portal.bap.get_report('A2_1_3_ForestCert', country='Austria')
        self.assertTrue(hasattr(record, 'FSCArea'))

    def test_A2_1_4(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('What Good Agricultural and Environmental Conditions (GAEC)'))

        record = self.portal.bap.get_report('A2_1_4', country='Austria')
        self.assertTrue(hasattr(record, 'Livestock'))

    def test_A2_1_6(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_6')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Have training or advisory services been specifically designed'))

        record = self.portal.bap.get_report('A2_1_6', country='Austria')
        self.assertTrue(hasattr(record, 'Training'))

    def test_A2_1_8(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_8')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_1_8', country='Austria')
        self.assertTrue(hasattr(record, 'RegBirds'))

    def test_A2_1_9(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_9')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('What was the amount of resources generated'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_1_9', country='Austria')
        self.assertTrue(hasattr(record, 'Percentage'))

    def test_A2_1_11(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_11')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Has a national strategy and/or action plan'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_1_11_NatStrats', country='Austria')
        self.assertTrue(hasattr(record, 'NatStratNo'))

        record = self.portal.bap.get_report('A2_1_11_RDPPayments', country='Austria')
        self.assertTrue(hasattr(record, 'EAFRD'))

    def test_A2_1_12(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A2_1_12')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('EAFRD'))
        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_1_12', country='France')
        self.assertTrue(hasattr(record, 'EAFRDTotal'))

    def test_A2_1_15(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_1_15')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Have national guidelines been developed'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_1_15', country='Austria')
        self.assertTrue(hasattr(record, 'Deforest'))

    def test_A2_2_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_2_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Have national monitoring programs'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_2_1', country='Austria')
        self.assertTrue(hasattr(record, 'NatMonitor'))

    def test_A2_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A2_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Oxygen Demand (BOD5) and ammonium concentrations'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_3_FWHabitatStatus', country='Austria')
        self.assertTrue(hasattr(record, 'FVNum'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_3_FWQuality', country='Austria')
        self.assertTrue(hasattr(record, 'BOD2002'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_3_InlandBathing', country='Austria')
        self.assertTrue(hasattr(record, 'Total2005'))


    def test_A2_3_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_3_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Number of monitoring stations in protected areas'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_3_1_Stations', country='Austria')
        self.assertTrue(hasattr(record, 'num'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_3_1_BioAsses', country='Austria')
        self.assertTrue(hasattr(record, 'GrnTransMA'))


    def test_A2_4_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A2_4_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertTrue(datatable.tr.th.text.startswith('Number of existing installations where IPPC permits'))

        datatable = soup.find('table', attrs={'class':'datatable'})
        record = self.portal.bap.get_report('A2_4_1', country='Austria')
        self.assertTrue(hasattr(record, 'NumPermitsNotUpdated'))

    def test_A2_4_2(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A2_4_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Comparison of Member States Emission ceilings with Member States current emissions and WM projections 2010')
        record = self.portal.bap.get_report('A2_4_2_EcoAtRisk', country='France')
        self.assertTrue(hasattr(record, 'Acid2000'))
        record = self.portal.bap.get_report('A2_4_2_Emission', country='France')
        self.assertTrue(hasattr(record, 'NO2006'))

    def test_A2_4_3(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A2_4_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Nitrogen balance expressed as kg nitrogen per hectare of total agricultural land')
        record = self.portal.bap.get_report('A2_4_3', country='France')
        self.assertTrue(hasattr(record, 'Y1990_1992'))

    def test_A3_1(self):
        self.browser.go('http://localhost/portal/countries/france/bap/target?id=A3_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Narrative summary of the above information (text provided should be able to stand alone) and any further details were available (e.g. types of marine and coastal habitat present, trends in status):')
        record = self.portal.bap.get_report('A3_1', country='France')
        self.assertTrue(hasattr(record, 'MarineFVNum'))

    def test_A3_1_4(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_1_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has the Member State established a programme of measures for coastal areas under the WFD? (Mark one only)')
        record = self.portal.bap.get_report('A3_1_4', country='France')
        self.assertTrue(hasattr(record, 'MeasureNo'))

    def test_A3_1_5(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_1_5')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'What is the status of your national plan/strategy for integrated coastal zone management (ICZM) (Mark one only)')
        record = self.portal.bap.get_report('A3_1_5', country='France')
        self.assertTrue(hasattr(record, 'NoPlan'))

    def test_A3_2(self):
        self.browser.go('http://localhost/portal/countries/france/bap/target?id=A3_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, '% of coastal bathing waters meeting minimum (mandatory) and guideline standards')
        record = self.portal.bap.get_report('A3_2_Phospate', country='France')
        self.assertTrue(hasattr(record, 'CountryRegion'))
        record = self.portal.bap.get_report('A3_2_Nitrogen', country='France')
        self.assertTrue(hasattr(record, 'CountryRegion'))
        record = self.portal.bap.get_report('A3_2_BathingWater', country='France')
        self.assertTrue(hasattr(record, 'Guide2006'))

    def test_A3_4(self):
        self.browser.go('http://localhost/portal/countries/france/bap/target?id=A3_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Amount of funding')
        record = self.portal.bap.get_report('A3_4', country='France')
        self.assertTrue(hasattr(record, 'Ax12007MS'))

    def test_A3_5(self):
        self.browser.go('http://localhost/portal/countries/france/bap/target?id=A3_5')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Percentage of stocks within safe biological limits')
        record = self.portal.bap.get_report('A3_5', country='France')
        self.assertTrue(hasattr(record, 'WithinLimit'))

    def test_A3_5_1(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_5_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Number of serious infringement procedures by year')
        record = self.portal.bap.get_report('A3_5_1', country='France')
        self.assertTrue(hasattr(record, 'vessels2006'))

    def test_A3_5_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A3_5_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Please indicate for which species a management plan exists (enter Y/N) and provide a link if possible')
        record = self.portal.bap.get_report('A3_5_2', country='France')
        self.assertTrue(hasattr(record, 'SalmonPlan'))

    def test_A3_5_3(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_5_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Fleet capacity (number of vessels, tonnage, power)')
        record = self.portal.bap.get_report('A3_5_3', country='France')
        self.assertTrue(hasattr(record, 'Vessel1999'))

    def test_A3_6_1(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_6_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Please indicate the number of active vessels, total number of infringements, number of type D infringements, total number of penalties, and average and maximum fines imposed for 2006 and 2007 if available.')
        record = self.portal.bap.get_report('A3_6_1', country='France')
        self.assertTrue(hasattr(record, 'vessel2006'))

    def test_A3_6_2(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_6_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Do you have a monitoring programme for sharks or seabirds? Enter Y/N.If Y, please indicate the first year of implementation (or expected implementation) and the number of years the programme is expected to run for.')
        record = self.portal.bap.get_report('A3_6_2', country='France')
        self.assertTrue(hasattr(record, 'SharkMonitor'))

    def test_A3_6_3(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_6_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'How many marine N2000 sites has the MS established?')
        record = self.portal.bap.get_report('A3_6_3_Inshore', country='France')
        self.assertTrue(hasattr(record, 'Number'))
        record = self.portal.bap.get_report('A3_6_3_Offshore', country='France')
        self.assertTrue(hasattr(record, 'Number'))

    def test_A3_7_1(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A3_7_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has the Member State established a multi-annual plan Data Collection Framework (DCF) that includes sampling/monitoring design for collecting ecosystem data to assist with assessing the impact of the fisheries sector on the marine ecosystem? (Enter Y/N)')
        record = self.portal.bap.get_report('A3_7_1', country='France')
        self.assertTrue(hasattr(record, 'DCF'))

    def test_A4_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A4_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Are you obliged by law to consider ecological networks in spatial planning? Enter Y or N here:')
        record = self.portal.bap.get_report('A4_3', country='Austria')
        self.assertTrue(hasattr(record, 'Planing'))

    def test_A4_4_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A4_4_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has your country implemented the CBD Guidelines on Sustainable Tourism? Enter Y or N here:')
        record = self.portal.bap.get_report('A4_4_1', country='Austria')
        self.assertTrue(hasattr(record, 'TourismGuide'))

    def test_A4_5_1(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A4_5_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Do you include biodiversity concerns into Regional and territorial development activities and programmes for Outermost regions? Enter Y or N here:')
        record = self.portal.bap.get_report('A4_5_1', country='France')
        self.assertTrue(hasattr(record, 'OutermostRegion'))

    def test_A5_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A5_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Number of worst invasive alien species registered per country')
        record = self.portal.bap.get_report('A5_1_AlienSpecies', country='Austria')
        self.assertTrue(hasattr(record, 'TotalAlien'))
        record = self.portal.bap.get_report('A5_1_AlienLegal', country='Austria')
        self.assertTrue(hasattr(record, 'General'))

    def test_A5_1_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A5_1_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Have a strategy and/or action plan on IAS been develop?Please mark accordingly:')
        record = self.portal.bap.get_report('A5_1_2', country='Austria')
        self.assertTrue(hasattr(record, 'StrategyNo'))

    def test_A5_1_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A5_1_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, "Has the country ratified the International Convention for the Control and Management of Ship's Ballast Water and Sediments under the International Maritime Organisation?Please enter Y or N here:")
        record = self.portal.bap.get_report('A5_1_3', country='Austria')
        self.assertTrue(hasattr(record, 'Ballast'))

    def test_A5_1_4(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A5_1_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Is there an inventory/database of alien species in place other than those published by the DAISIE and/or NOBANIS projects?Please tick only one box:')
        record = self.portal.bap.get_report('A5_1_4', country='Austria')
        self.assertTrue(hasattr(record, 'DatabaseNo'))

    def test_A5_2_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A5_2_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has legislation on co-existence of genetically modified crops with conventional and organic farming been adopted?Please tick only one box:')
        record = self.portal.bap.get_report('A5_2_2', country='Austria')
        self.assertTrue(hasattr(record, 'GMlegalNo'))

    def test_A6_1_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A6_1_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has your country submitted the 4thnational report to the Convention on Biological Diversity (submitted= Y, not submitted=N)?')
        record = self.portal.bap.get_report('A6_1_1', country='Austria')
        self.assertTrue(hasattr(record, 'NationalReport4'))

    def test_A7_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A7_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Annual spending on biodiversity-relatedmultilateralaid')
        record = self.portal.bap.get_report('A7_1', country='Austria')
        self.assertTrue(hasattr(record, 'Aid2006'))

    def test_A7_1_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A7_1_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Annual spending on biodiversity-relatedbilateralaid')
        record = self.portal.bap.get_report('A7_1_3', country='Austria')
        self.assertTrue(hasattr(record, 'BiAid2006'))

    def test_A7_1_4(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A7_1_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Contribution to the GEF replenishment')
        record = self.portal.bap.get_report('A7_1_4', country='Austria')
        self.assertTrue(hasattr(record, 'Total3rd'))

    def test_A7_1_6(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A7_1_6')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Annual spending on biodiversity-relatedbilateralaid')
        #record = self.portal.bap.get_report('A7_1_6', country='France')
        #self.assertTrue(hasattr(record, 'XXX'))

    def test_A7_2_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A7_2_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Are ex-ante strategic environmental assessment (SEA) of relevant strategies and programmes and environmental impact assessment (EIA) of relevant projects mandatory?Please enter Y or N:')
        record = self.portal.bap.get_report('A7_2_2', country='Austria')
        self.assertTrue(hasattr(record, 'MandatorySEA_EIA'))

    def test_A7_2_5(self):
        self.browser.go('http://localhost/portal/countries/france/bap/action?id=A7_2_5')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Are ex-ante strategic environmental assessment (SEA) of relevant strategies and programmes and environmental impact assessment (EIA) of relevant projects mandatory for OCTs?Please enter Y or N:')
        #record = self.portal.bap.get_report('A7_2_5', country='France')
        #self.assertTrue(hasattr(record, 'XXX'))

    def test_A8_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A8_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'The MS actions under this target fully implemented by 2010, showing impact on biodiversity of EU trade significantly reduced by 2010 (Y/N)')
        record = self.portal.bap.get_report('A8_1', country='Austria')
        self.assertTrue(hasattr(record, 'A8_1_3Imp'))

    def test_A8_1_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A8_1_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Indicate the provision of funds for the CBD Access & Benefit-sharing Working Group')
        record = self.portal.bap.get_report('A8_1_3_CBD', country='Austria')
        self.assertTrue(hasattr(record, 'Y2006'))
        record = self.portal.bap.get_report('A8_1_3_BenefitShare', country='Austria')
        self.assertTrue(hasattr(record, 'Legal'))
        record = self.portal.bap.get_report('A8_1_3_GeneticResource', country='Austria')
        self.assertTrue(hasattr(record, 'Legal'))

    def test_A8_1_4(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A8_1_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        '''<em> and <br/> tags are not displayed on the page, so this is why
        no space between national and biodiversity:'''
        self.assertEqual(datatable.tr.th.text, 'What is the proportion of national consumption of wood products derived from sustainable sources (%)?')
        record = self.portal.bap.get_report('A8_1_4', country='Austria')
        self.assertTrue(hasattr(record, 'Y2006'))

    def test_A8_1_8(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A8_1_8')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        '''<em> and <br/> tags are not displayed on the page, so this is why
        no space between national and biodiversity:'''
        self.assertEqual(datatable.tr.th.text, 'Number of import applications denied during the last reporting cycle compared to the number of import documents issued')
        record = self.portal.bap.get_report('A8_1_8', country='Austria')
        self.assertTrue(hasattr(record, 'ImportApps'))

    def test_A9_1_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A9_1_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        '''<em> and <br/> tags are not displayed on the page, so this is why
        no space between national and biodiversity:'''
        self.assertEqual(datatable.tr.th.text, 'Annual anthropogenic Greenhouse Gas Emissions (GHG) in million tonnes of CO2 equivalents (excl. LULUCF).')
        record = self.portal.bap.get_report('A9_1_1', country='Austria')
        self.assertTrue(hasattr(record, 'GHG2006'))

    def test_A9_3_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A9_3_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        '''<em> and <br/> tags are not displayed on the page, so this is why
        no space between national and biodiversity:'''
        self.assertEqual(datatable.tr.th.text, 'Have a separate action plan onbiomassand/or a National Renewable Action Plan (NREAP) already been developed?Please tick only one box for each row:')
        record = self.portal.bap.get_report('A9_3_2', country='Austria')
        self.assertTrue(hasattr(record, 'PlanNo'))

    def test_A9_4_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A9_4_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        '''<em> and <br/> tags are not displayed on the page, so this is why
        no space between national and biodiversity:'''
        self.assertEqual(datatable.tr.th.text, 'Have a nationalbiodiversity adaptation strategyand/oraction planbeen developed?Please mark accordingly:')
        record = self.portal.bap.get_report('A9_4_1', country='Austria')
        self.assertTrue(hasattr(record, 'StratNo'))

    def test_A9_4_3(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A9_4_3')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Have scientific studies been undertaken to support assessments of species and habitats at risk?Please enter Y or N and provide comments')
        record = self.portal.bap.get_report('A9_4_3', country='Austria')
        self.assertTrue(hasattr(record, 'StudiesYN'))

    def test_A10_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=A10_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Is there a national research programme dedicated exclusively to supporting biodiversity research? Enter Y or N here:')
        record = self.portal.bap.get_report('A10_1', country='Austria')
        self.assertTrue(hasattr(record, 'Programme'))

    def test_A10_1_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A10_1_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Is there a plan for follow-up to MA as part of a national initiative? Y or N here:')
        record = self.portal.bap.get_report('A10_1_2', country='Austria')
        self.assertTrue(hasattr(record, 'NatFollow'))

    def test_A10_1_8(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A10_1_8')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has a national biodiversity platform been created to ensure that biodiversity research and outcomes are reflected in policy development and implementation? Enter Y or N here:')
        record = self.portal.bap.get_report('A10_1_8', country='Austria')
        self.assertTrue(hasattr(record, 'Platform'))

    def test_A10_1_9(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=A10_1_9')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Please indicate level of participation in the Global Biodiversity Information Facility (GBIF). Please select only ONE of the following:')
        record = self.portal.bap.get_report('A10_1_9', country='Austria')
        self.assertTrue(hasattr(record, 'MoU'))

    def test_B1_1_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B1_1_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Does a national programme identifying long-term goals and the allocation of funding (both COM and MS co-funding) for the related biodiversity activities exist? If present indicate Y, if absent indicate N')
        record = self.portal.bap.get_report('B1_1_1', country='Austria')
        self.assertTrue(hasattr(record, 'NatProg'))

    def test_B1_1_4(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B1_1_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, "Indicate cohesion and structural funds for projects directly or indirectly providing biodiversity benefits in all MS' operational programmes (in EUR)")
        record = self.portal.bap.get_report('B1_1_4', country='Austria')
        self.assertTrue(hasattr(record, 'Cat51_2006'))

    def test_B1_1_8(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B1_1_8')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Please indicate amount of national funding allocated for European and national biodiversity research activities and programmes for the years indicated.')
        record = self.portal.bap.get_report('B1_1_8', country='Austria')
        self.assertTrue(hasattr(record, 'Y2006'))

    def test_B2_4(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=B2_4')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has a new national environmental policy or strategy been created, or an existing policy or strategy updated, in light of the Communication \'Halting the loss of biodiversity by 2010 and beyond\'? Please indicate Y or N in each case.')
        record = self.portal.bap.get_report('B2_4', country='Austria')
        self.assertTrue(hasattr(record, 'New'))

    def test_B3_1_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B3_1_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'How many farming and biodiversity, forestry and biodiversity partnerships have been facilitated by MS at the local, regional and national levels? Please indicate number of partnerships in the following table:')
        record = self.portal.bap.get_report('B3_1_2', country='Austria')
        self.assertTrue(hasattr(record, 'Local'))

    def test_B3_1_5(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B3_1_5')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Does MS have a forum or similar platform/framework set up for biodiversity and planning partnership at local, regional, national levels? Please indicate Y/N against each box')
        record = self.portal.bap.get_report('B3_1_5', country='Austria')
        self.assertTrue(hasattr(record, 'Local'))

    def test_B3_1_6(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B3_1_6')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'How many forums or similar platforms/frameworks have been set up by MS to encourage business biodiversity partnerships? Please indicate number of forums/partnerships in the following table:')
        record = self.portal.bap.get_report('B3_1_6', country='Austria')
        self.assertTrue(hasattr(record, 'Y2006'))

    def test_B3_1_7(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B3_1_7')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'How many forums or similar platform/framework set up to encourage partnerships between financing sector and biodiversity? Please indicate number of forums or similar platforms/frameworks in the following table:')
        record = self.portal.bap.get_report('B3_1_7', country='Austria')
        self.assertTrue(hasattr(record, 'Y2006'))

    def test_B3_1_8(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B3_1_8')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Have the CBD Akwe-Kwon Guidelines been applied to projects financed by public funds? Please indicate Y/N against each box:')
        record = self.portal.bap.get_report('B3_1_8', country='Austria')
        self.assertTrue(hasattr(record, 'EU'))

    def test_B4_1_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B4_1_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Has a communications campaign in support of the EU Biodiversity Action Plan (BAP) been developed at the national level?Please tick only one of the following')
        record = self.portal.bap.get_report('B4_1_1', country='Austria')
        self.assertTrue(hasattr(record, 'Yes'))

    def test_B4_1_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=B4_1_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'What is the amount of funding by the MS for the supporting the 2010 countdown initiative?Please indicate amounts (in EUR):')
        record = self.portal.bap.get_report('B4_1_2', country='Austria')
        self.assertTrue(hasattr(record, 'Y2006'))

    def test_C1_2(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/target?id=C1_2')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Indicate the extent to which the full suite of SEBI and national indicators is developed and applied:')
        record = self.portal.bap.get_report('C1_2', country='Austria')
        self.assertTrue(hasattr(record, 'SEBI'))

    def test_C1_2_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=C1_2_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Indicate national/sub-national biodiversity indicators')
        record = self.portal.bap.get_report('C1_2_1', country='Austria')
        self.assertTrue(hasattr(record, 'Abundance'))

    def test_C1_3_1(self):
        self.browser.go('http://localhost/portal/countries/austria/bap/action?id=C1_3_1')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        datatable = soup.find('table', attrs={'class':'datatable'})
        self.assertEqual(datatable.tr.th.text, 'Indicate national/sub-national biodiversity monitoring schemes for habitats')
        record = self.portal.bap.get_report('C1_3_1', country='Austria')
        self.assertTrue(hasattr(record, 'Costal'))
