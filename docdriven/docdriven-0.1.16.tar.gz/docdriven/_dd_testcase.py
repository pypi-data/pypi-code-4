import unittest
# import types
# import requests
# import json
from .. import interface
import time
import datetime
import copy
import logging
import sys

from _dd_testcase_util import merge_struct, log1, log2, log3, build_path, get, post
from _dd_testcase_util import log_js_example, is_compatible_json, deal_with_output_response_data

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)10s - %(levelname)7s - %(message)s',"%m-%d %H:%M")
ch.setFormatter(formatter)
# log.addHandler(ch)

class DocDrivenTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.global_config = {}
        cls.global_predict = {}
        cls.runtime_config = {}
        cls.runtime_predict = {}
        # build the test method for the introduction, then call it.
        if cls.driven_doc.introduction:
            cls.global_config = cls.driven_doc.introduction.get_json_section(interface.CONFIG)
            cls.global_predict = cls.driven_doc.introduction.get_json_section(interface.PREDICT)
            cls.run_route_list(cls.driven_doc.introduction.route_list, cls.global_config, cls.global_predict)

    @classmethod
    def tearDownClass(cls):
        if cls.driven_doc.conclusion:
            conc_config  = cls.driven_doc.conclusion.get_json_section(interface.CONFIG)
            conc_predict = cls.driven_doc.conclusion.get_json_section(interface.PREDICT)
            cls.run_route_list(cls.conclusion.route_list, conc_config, conc_predict)

    @classmethod
    def run_route_list(cls, route_list, ch_config, ch_predict):
        full_chapter_config = copy.deepcopy(cls.global_config)
        full_chapter_config = merge_struct(full_chapter_config, ch_config)

        full_chapter_predict = copy.deepcopy(cls.global_predict)
        full_chapter_predict = merge_struct(full_chapter_predict, ch_predict)

        for route in route_list:
            cls.run_route(route, full_chapter_config, full_chapter_predict)

    @classmethod
    def go_route(cls, route, config):
        route.report_stamp('FAIL', 1, datetime.datetime.now(), speed=0.0)
        path = build_path(route.title, config)
        start_time = None
        result = {}
        if config.get('post'): # will return None if json has null for this key
            start_time = time.time()
            result = post(path, config['post'], DocDrivenTestCase.default_base_url, DocDrivenTestCase.default_http_headers)
            speed = time.time() - start_time
        else:
            start_time = time.time()
            result = cls.GET(path)
            speed = time.time() - start_time
        return result, speed

    @classmethod
    def run_route(cls, route, full_ch_config, full_ch_predict):
        full_config = copy.deepcopy(full_ch_config)
        route_config = route.get_json_section(interface.CONFIG)
        full_config = merge_struct(full_config, route_config)
        full_config = merge_struct(full_config, cls.runtime_config)

        full_predict = copy.deepcopy(full_ch_predict)
        route_predict = route.get_json_section(interface.PREDICT)
        full_predict = merge_struct(full_predict, route_predict)
        full_predict = merge_struct(full_predict, cls.runtime_predict)

        log_string = ''
        log_string += log1(route, full_config, full_predict)

        result, speed_in_sec = cls.go_route(route, full_config)

        if result.status_code>=200 and result.status_code<300:
            log.debug('got report code 2xx')
            route.report_stamp('START', 2, datetime.datetime.now(), speed=speed_in_sec)
        else:
            log.debug('got report code: '+str(result.status_code))
            route.report_stamp('HTTP-'+str(result.status_code), 1, datetime.datetime.now(), speed=speed_in_sec)

        actual_response = result.json()
        log.debug('actual_response: '+str(actual_response))
        output_response = copy.deepcopy(actual_response)

        if actual_response[full_config['route_success_flag']]:
            route.report_stamp('OKAYFLAG', 3, datetime.datetime.now(), speed=speed_in_sec) # keeping track of speed always...

        compatible = is_compatible_json(actual_response, full_predict)
        if compatible:
            route.report_stamp('SUCCESS', 4, datetime.datetime.now(), speed=speed_in_sec)
        else:
            route.report_stamp('INCOMPAT', 2, datetime.datetime.now(), speed=speed_in_sec)

        # if we have been given instructions on what to do with the response data
        resp_instr = full_config.get('response')
        if resp_instr:
            log_string = deal_with_output_response_data(route, compatible, output_response, resp_instr, log_string)
        else:
            log.debug('no response key in the config')

        log_string += log3(route)
        log_js_example(route, full_config, output_response)

        cls.runtime_config, cls.runtime_predict = route.runtime_exec(actual_response)

        log.debug('\n'+log_string)
        return actual_response

    @classmethod
    def insert_test_method(cls, chapter):
        test_name = 'test_'+chapter.title.lower()
        test_name = test_name.replace(' ', '_')
        test_name = test_name.replace(',', '_')
        test_name = test_name.replace('.', '_')
        test_name = test_name.replace('/', '_')
        test_name = test_name.replace("'", '_')
        test_name = test_name.replace('&', '_')
        test_mthd = cls.build_test_method(chapter)
        log.debug('injecting: '+test_name)
        setattr(cls, test_name, test_mthd)

    @classmethod
    def build_test_method(cls, chapter):
        chp = chapter
        def test_method(self):
            # log.debug('in test method for chapter: '+chp.title)
            ch_config  = chp.get_json_section(interface.CONFIG)
            ch_predict = chp.get_json_section(interface.PREDICT)
            DocDrivenTestCase.run_route_list(chp.route_list, ch_config, ch_predict)
            log.debug('finished running route list for chapter: '+chp.title)
        return test_method


