# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.devtools.testlib import CubicWebTC

class TestQuappli(CubicWebTC):
    def setup_database(self):
        super(TestQuappli, self).setup_database()
        ce = self.request().create_entity
        self.my_queue = ce('ResourceQueue', name=u'my queue')
        self.my_host_1 = ce('Host', name=u'my first host', 
                            reverse_has_resources=self.my_queue)
        self.my_host_2 = ce('Host', name=u'my second host', 
                            reverse_has_resources=self.my_queue)
        self.my_run_1 = ce('Run', name=u'my first run')
        self.my_run_2 = ce('Run', name=u'my second run')
        self.my_run_3 = ce('Run', name=u'my third run')
        self.my_run_4 = ce('Run', name=u'my fourth run')
        self.commit()

    def test_basic_quappli(self):
        self.my_queue.append(self.my_run_1) # equivalent to my_queue.insert(0, my_run_1)
        self.my_queue.append(self.my_run_2) # equivalent to my_queue.insert(1, my_run_2)
        self.my_queue.append(self.my_run_3)
        self.commit()

        self.my_queue.remove(self.my_run_2)
        self.commit()

        self.my_queue.run()
        self.commit()

        self.my_queue.pause()
        self.commit()

        self.my_run_1.cw_adapt_to('Queueable').release_resource()
        self.commit()

        self.my_queue.insert(1, self.my_run_4) # my_run_4 right after my_run_1
        self.commit()


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

