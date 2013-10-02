import unittest
from g2g.engine import Engine
import g2g.engine
from g2g import g2g_config
from g2g.logtype.grinder import transaction
from g2g.aggregator.http import HTTPAggregator
from g2g.aggregator.non_http import NonHTTPAggregator
from os.path import expanduser
import os

_ROOT_DIR = os.getcwd()
if _ROOT_DIR.endswith("test"):
    _ROOT_DIR = _ROOT_DIR[:len(_ROOT_DIR) - 5]
HOME = expanduser("~")
DATA_LINE = "3, 0, 1, 1364113903424, 29, 0, 200, 177, 0, 3, 4, 13, 1"
HTTP_WORDS = DATA_LINE.split(", ")
NON_HTTP_WORDS = HTTP_WORDS[:6]
NON_HTTP_MAPPING_FILE = "%s/test/data/non-http.mapping" % _ROOT_DIR
NON_HTTP_DATA_FILE = "%s/test/data/non-http.data" % _ROOT_DIR
HTTP_DATA_FILE = "%s/test/data/http.data" % _ROOT_DIR
HTTP_MAPPING_FILE = "%s/test/data/http.mapping" % _ROOT_DIR
END_TIMESTAMP = 1000000


class MockAggregator(object):
    def __init__(self):
        self.tx_data_map = {}
        self.report_time = 999999999999

    def add_transaction(self, tx_name, tx_data):
        #print "Adding data for tx name %s" % tx_name
        if tx_name not in self.tx_data_map:
            self.tx_data_map[tx_name] = []
        self.tx_data_map[tx_name].append(tx_data)

    def report_to_graphite(self):
        pass


class TestEngine(unittest.TestCase):

    def _create_tmp_file(self, file_name):
        if os.path.exists(file_name):
            return
        f = open(file_name, "w")
        f.write(".")
        f.close()

    def _delete_tmp_file(self, file_name):
        if os.path.exists(file_name):
            os.remove(file_name)

    def setUp(self):
        self.configfile = "test_engine.delete.me"
        g2g_config.create_example_config_file(self.configfile)
        self.config = g2g_config.get_config([self.configfile])
        self.config.data_file = HTTP_DATA_FILE
        self.config.mapping_file = HTTP_MAPPING_FILE

    def tearDown(self):
        if os.path.exists(self.configfile):
            os.remove(self.configfile)
        engine = Engine(self.config)
        offset_file = engine._get_offset_file(self.config.data_file)
        if os.path.exists(offset_file):
            os.remove(offset_file)

    def test_get_offset_file(self):
        # missing data file
        engine = Engine(self.config)
        of = engine._get_offset_file("/etc/hosts.fake")
        self.assertIsNone(of)

        # data file is relative path in current dir
        data_file = "delete.me"
        self._create_tmp_file(data_file)
        of = engine._get_offset_file(data_file)
        self.assertEqual(of, g2g_config.DOTDIR + os.sep + data_file + ".offset")
        self._delete_tmp_file(data_file)

        # data file is relative path in current dir
        root_dir = "deleteme"
        filename = "xyz"
        os.mkdir(root_dir)
        data_file = root_dir + os.sep + filename
        self._create_tmp_file(data_file)
        of = engine._get_offset_file(data_file)
        self.assertEqual(of, g2g_config.DOTDIR + os.sep + root_dir + "." + filename + ".offset")
        self._delete_tmp_file(data_file)
        os.rmdir(root_dir)

        # data file is absolute path
        data_file = "/etc/hosts"
        self._create_tmp_file(data_file)
        of = engine._get_offset_file(data_file)
        self.assertEqual(of, g2g_config.DOTDIR + os.sep + "etc.hosts.offset")

    def test_get_first_data_line(self):
        engine = Engine(self.config)
        first = "0, 0, 1, 1364113903422, 0, 0, 0, 0, 0, 0, 0, 0, 0\n"
        with self.assertRaises(SystemExit) as cm:
            engine._get_first_data_line("nonexistent_file")
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(engine._get_first_data_line(HTTP_DATA_FILE), first)

    def test_get_timestamp(self):
        engine = Engine(self.config)
        self.assertEqual(engine._get_timestamp(HTTP_WORDS), 1364113903)
        self.assertIsNone(engine._get_timestamp([]))

    def test_is_grinder_log_http(self):
        engine = Engine(self.config)
        self.assertTrue(engine._is_grinder_log_http(HTTP_DATA_FILE))
        self.assertFalse(engine._is_grinder_log_http(NON_HTTP_DATA_FILE))
        with self.assertRaises(SystemExit) as cm:
            engine._is_grinder_log_http("nonexistent.file")
        self.assertEqual(cm.exception.code, 1)

    def test_ingest_log_resume(self):
        initial_ingests = g2g.engine._ingest_invocations
        self.config.resume = True
        engine = Engine(self.config)
        offset_file = engine._get_offset_file(self.config.data_file)
        self.assertFalse(os.path.exists(offset_file))
        engine.ingest_log(test_mode=True)
        self.assertTrue(os.path.exists(offset_file))
        os.remove(offset_file)
        self.config.resume = False
        engine = Engine(self.config)
        self.assertEqual(g2g.engine._ingest_invocations - initial_ingests, 1)
        timestamps = engine.ingest_log(test_mode=True)
        #self.assertFalse(os.path.exists(offset_file))
        self.assertEqual(g2g.engine._ingest_invocations - initial_ingests, 2)
        self.assertLess(136411390, timestamps[1])
        self.assertEqual(timestamps[0], 1364113903422 / 1000)  # first ts in data file

    def test_ingest_log_follow(self):
        initial_ingests = g2g.engine._ingest_invocations
        self.config.follow = False
        self.config.follow_interval_seconds = 0.001
        engine = Engine(self.config)
        engine.ingest_log(test_mode=True)
        self.assertEqual(g2g.engine._ingest_invocations - initial_ingests, 1)
        initial_ingests = g2g.engine._ingest_invocations
        self.config.follow = True
        engine = Engine(self.config)
        engine.ingest_log(test_mode=True)
        self.assertEqual(g2g.engine._ingest_invocations - initial_ingests, 2)

    def test_ingest_log_http(self):
        engine = Engine(self.config)  # HTTP by default
        self.assertEqual(engine.aggregator_class, HTTPAggregator)
        self.assertEqual(engine.grinder_transaction_class, transaction.HTTPTest)
        self.config.data_file = NON_HTTP_DATA_FILE
        self.config.mapping_file = NON_HTTP_MAPPING_FILE
        engine = Engine(self.config)
        self.assertEqual(engine.aggregator_class, NonHTTPAggregator)
        self.assertEqual(engine.grinder_transaction_class, transaction.NonHTTPTest)

    def test_ingest_log_private_http(self):
        mock_aggregator = MockAggregator()
        engine = Engine(self.config)
        engine._ingest_log(mock_aggregator, test_mode=True)
        # there are two types of transactions in the HTTP log:
        #    'Search_No_Match',  'Search_Magic_Key'
        self.assertTrue("Search_No_Match" in mock_aggregator.tx_data_map)
        self.assertTrue("Search_Magic_Key" in mock_aggregator.tx_data_map)
        self.assertFalse("All_Transactions" in mock_aggregator.tx_data_map)
        self.assertEqual(len(mock_aggregator.tx_data_map), 2)
        self.assertEqual(len(mock_aggregator.tx_data_map["Search_No_Match"]), 97)
        self.assertEqual(len(mock_aggregator.tx_data_map["Search_Magic_Key"]), 2)
        # the 5th tx in the http data log has response time 29 ms
        self.assertEqual(mock_aggregator.tx_data_map["Search_No_Match"][5].time, 29)
        self.assertEqual(mock_aggregator.tx_data_map["Search_No_Match"][6].new_connections, 1)

'''
    def test_ingest_log_private_non_http(self):
        self.fail("TODO")

    def test_ingest_log_private_resume(self):
        self.fail("TODO")
'''
