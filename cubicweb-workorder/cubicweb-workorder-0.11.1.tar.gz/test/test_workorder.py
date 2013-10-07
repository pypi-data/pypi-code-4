"""template automatic tests"""

from datetime import date, timedelta
from logilab.common.testlib import unittest_main

from cubicweb.devtools.testlib import AutomaticWebTest, CubicWebTC

class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Order', 'WorkOrder'))

    def list_startup_views(self):
        return ()

class BasicEntitiesTC(CubicWebTC):

    def setup_database(self):
        """
        create 1 Order and 3 WorkOrder
        """
        req = self.request()
        # WorkOrder
        self.woben = req.create_entity('WorkOrder', title=u'Ben',
                                       begin_date=date(2001, 9, 11),
                                       end_date=date(2011, 5, 2)).eid
        self.woempty = req.create_entity('WorkOrder', title=u'Empty').eid
        self.woforrest = req.create_entity('WorkOrder', title=u'Forrest',
                                          begin_date=date.today() - timedelta(1),
                                          end_date=date.today() + timedelta(15)).eid
        # Order
        self.order = req.create_entity('Order', title=u'Coltrane', budget=100.0,
                                       split_into=(self.woben, self.woforrest,
                                                   self.woempty)).eid

    def test_milestone_adapter(self):
        req = self.request()
        # Test dates of an empty workorder.
        empty = req.entity_from_eid(self.woempty)
        ms_empty = empty.cw_adapt_to('IMileStone')
        self.assertEqual(ms_empty.initial_prevision_date(),
                         date.today())

        # Test dates of an passed workorder, i.e. end date < today.
        ben = req.entity_from_eid(self.woben)
        ms_ben = ben.cw_adapt_to('IMileStone')
        self.assertEqual(ms_ben.initial_prevision_date(),
                         ben.end_date)
        self.assertEqual(ms_ben.eta_date(), date.today())

        # Test dates of an 'in progress' (not the state!) workorder, i.e. end
        # date > today
        forrest= req.entity_from_eid(self.woforrest)
        ms_forrest = forrest.cw_adapt_to('IMileStone')
        self.assertEqual(ms_forrest.initial_prevision_date(),
                         forrest.end_date)
        self.assertEqual(ms_forrest.eta_date(),
                         forrest.end_date)



if __name__ == '__main__':
    unittest_main()
