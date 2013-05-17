from cubicweb.devtools import buildconfig
from cubicweb.devtools.testlib import RealDBTest

def setup_module(options):
    if options.dbname is None:
        raise Exception('the <dbname> options is required')
    RealDatabaseTC.configcls = buildconfig(options.dbuser, options.dbpassword,
                                           options.dbname, options.euser,
                                           options.epassword)

class RealDatabaseTC(RealDBTest):
    configcls = None # set by setup_module()

    def test_all_primaries(self):
        for rset in self.iter_individual_rsets(limit=50):
            yield self.view, 'primary', rset, rset.req.reset_headers()

    def test_startup_views(self):
        for vid in self.list_startup_views():
            req = self.request()
            yield self.view, vid, None, req


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
