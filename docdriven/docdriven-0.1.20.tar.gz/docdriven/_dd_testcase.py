import unittest
import datetime
import copy
import logging
import sys
import pprint
from jsonschema import validate

import interface
from _dd_testcase_util import merge_struct, log1, log3, log_js_example, go_route
from _dd_testcase_util import is_compatible_json, deal_with_output_response_data
import _dd_testcase_util

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
            cls.run_route_list(cls.driven_doc.conclusion.route_list, conc_config, conc_predict)

    @classmethod
    def setUp(cls):
        cls.runtime_config = {}
        cls.runtime_schema_predict = {}
        cls.config_predict_response = []

    @classmethod
    def run_route_list(cls, route_list, ch_config, ch_predict):
        full_chapter_config = copy.deepcopy(cls.global_config)
        full_chapter_config = merge_struct(full_chapter_config, ch_config)

        full_chapter_predict = copy.deepcopy(cls.global_predict)
        full_chapter_predict = merge_struct(full_chapter_predict, ch_predict)

        for route in route_list:
            cls.run_route(route, full_chapter_config, full_chapter_predict)

    @classmethod
    def run_route(cls, route, full_ch_config, full_ch_predict):
        full_config = copy.deepcopy(full_ch_config)
        route_config = route.get_json_section(interface.CONFIG)
        full_config = merge_struct(full_config, route_config)
        if cls.runtime_config is not None:
            full_config = merge_struct(full_config, cls.runtime_config)

        schema_predict = copy.deepcopy(full_ch_predict)
        route_schema_predict = route.get_json_section(interface.PREDICT)
        schema_predict = merge_struct(schema_predict, route_schema_predict)
        if cls.runtime_schema_predict is not None:
            schema_predict = merge_struct(schema_predict, cls.runtime_schema_predict)

        # pprint.pprint(schema_predict)


        log_string = ''
        log_string += log1(route, full_config, schema_predict)

        result, speed_in_sec = go_route(route, full_config)

        if result.status_code>=200 and result.status_code<300:
            log.debug('got report code 2xx')
            route.report_stamp('START', 2, datetime.datetime.now(), speed=speed_in_sec)
        else:
            log.debug('got report code: '+str(result.status_code))
            route.report_stamp('HTTP-'+str(result.status_code), 1, datetime.datetime.now(), speed=speed_in_sec)

        if result.status_code >= 500 and result.status_code < 600:
            # there will be no json data if the server had an error, so we
            # immediately return in order to prevent throwing an exception
            # ourselves, which would prevent the rest of the routes from
            # being attempted -- routes that are further down may have
            # relied on this route being successful, so this section should
            # be removed before version 0.2
            return

        actual_response = result.json()
        output_response = copy.deepcopy(actual_response)

        success_flag = full_config.get('route_success_flag')
        if success_flag:
            if isinstance(actual_response, dict):
                if actual_response.get(success_flag):
                    route.report_stamp('OKAYFLAG', 3, datetime.datetime.now(), speed=speed_in_sec) # keeping track of speed always...
                else:
                    route.report_stamp('NOT-OKAY', 2, datetime.datetime.now(), speed=speed_in_sec) # keeping track of speed always...
            else:
                route.report_stamp('NOT-DICT', 2, datetime.datetime.now(), speed=speed_in_sec) # keeping track of speed always...)

        compatible = False
        note = ''
        try:
            validate(actual_response, schema_predict)
            compatible = True
        except Exception, e:
            lines = str(e).splitlines()
            count = 0
            for line in lines:
                if len(line.strip())>0:
                    note += line.strip()+'  -  '
                    count += 1
                    if count > 3: break
         # = is_compatible_json(actual_response, full_predict)

        if compatible:
            route.report_stamp('SUCCESS', 4, datetime.datetime.now(), speed=speed_in_sec)
            if speed_in_sec > 5:
                if speed_in_sec < 10:
                    printable_speed = str(round(speed_in_sec, 1))
                elif speed_in_sec >= 10 and speed_in_sec < 1000:
                    printable_speed = str(round(speed_in_sec, 0))
                else:
                    printable_speed = '!!!'
                route.report_stamp('SLOW-'+printable_speed, 3, datetime.datetime.now(), speed=speed_in_sec)
        else:
            route.report_stamp('INCOMPAT', 2, datetime.datetime.now(), speed=speed_in_sec, note=note)

        # if we have been given instructions on what to do with the response data
        resp_instr = full_config.get('response')
        if resp_instr:
            log.debug(resp_instr)
            log_string = deal_with_output_response_data(route, compatible, output_response, resp_instr, log_string)
        else:
            log.debug('no response key in the config')

        log_string += log3(route)
        log_js_example(route, full_config, output_response)

        cls.config_predict_response.append((full_config, schema_predict, actual_response))
        cls.runtime_config, cls.runtime_predict = route.runtime_exec(cls.config_predict_response)

        log.debug('\n'+log_string)
        print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n'
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

    @classmethod
    def remove_test_methods(cls):
        test_methods = []
        for name in vars(cls):
            if name.startswith("test_") and callable(getattr(cls, name)):
                test_methods.append(name)
        for test_method in test_methods:
            delattr(cls, test_method)

