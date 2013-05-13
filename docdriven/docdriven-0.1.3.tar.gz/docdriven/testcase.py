import unittest
import types
import requests
import json
import interface
import time
import datetime
import copy

class DocDrivenTestCase(unittest.TestCase):

    default_base_url='http://216.224.141.220:5438'
    default_http_headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    def __init__(self, driven_down_doc):
        self.driven_down_doc = driven_down_doc

    @classmethod
    def GET(cls, path, base_url=default_base_url, http_headers=default_http_headers):
        return requests.get(base_url+path, headers=http_headers)

    @classmethod
    def POST(cls, path, data, base_url=default_base_url, http_headers=default_http_headers):
        if not isinstance(data, str):
            data = json.dumps(data)
        return requests.post(base_url+path, data=data, headers=http_headers)

    @classmethod
    def setUpClass(cls):
        cls.global_config = {}
        cls.global_reply = {}
        cls.runtime_config = {}
        cls.runtime_reply = {}
        # build the test method for the introduction, then call it.
        if cls.ddd.introduction:
            cls.global_config = json.loads(
                cls.ddd.introduction.sections[interface.JS_CONFIG])
            cls.global_reply = json.loads(
                cls.ddd.introduction.sections[interface.JS_REPLY])
            cls.run_route_list(cls.ddd.introduction.route_list, cls.global_config, cls.global_reply)

    @classmethod
    def tearDownClass(cls):
        if cls.ddd.conclusion:
            conc_config = json.loads(
                cls.ddd.conclusion.sections[interface.JS_CONFIG])
            conc_reply = json.loads(
                cls.ddd.conclusion.sections[interface.JS_REPLY])
            cls.run_route_list(cls.conclusion.route_list, conc_config, conc_reply)


    @classmethod # there is recursion in this method
    def merge_struct(cls, base, local):
        if base is None:
            if local is not None:
                return local
            else:
                return None

        for key in local:
            if not key in base:
                base[key] = local[key]
            else:
                if isinstance(local[key], dict):
                    base[key] = cls.merge_struct(base[key], local[key])
                else:
                    base[key] = local[key]
        return base


    @classmethod
    def run_route_list(cls, route_list, ch_config, ch_predict):
        full_chapter_config = copy.deepcopy(cls.global_config)
        full_chapter_config = cls.merge_struct(full_chapter_config, ch_config)

        full_chapter_predict = copy.deepcopy(cls.global_predict)
        full_chapter_predict = cls.merge_struct(full_chapter_predict, ch_predict)

        for route in route_list:
            cls.run_route(route, full_chapter_config, full_chapter_predict)

    @classmethod
    def log1(cls, route, config, predict):
        print '\n========================================================================================='
        print 'running route: '+route.title+' '+datetime.datetime.now().isoformat()[11:19]
        print '========================================================================================='
        print '#### config'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json'
        print json.dumps(config, indent=4)
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '#### predict'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json'
        print json.dumps(predict, indent=4)
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

    @classmethod
    def log2(cls, route):
        print '#### response'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json'
        print json.dumps(json.loads(route.sections[interface.RESPONSE]), indent=4, separators=(',', ': '))
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

    @classmethod
    def log3(cls, route):
        print '#### status'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json'
        print json.dumps(json.loads(route.sections[interface.STATUS]), indent=4, separators=(',', ': '))
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '#### python'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  python'
        print json.dumps(json.loads(route.sections[interface.RUNTIME]), indent=4, separators=(',', ': '))
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

    @classmethod
    def log_js_example(cls, route, config, output_response):
        js = '\n**JAVASCRIPT**\n'
        js += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  javascript\n'
        js += 'post_json = {}\n'
        for key in config['post']:
            if isinstance(config['post'][key], (basestring, int, bool, types.NoneType)):
                js += 'post_json.'+key+' = "'+str(config['post'][key])+'";\n'
            elif isinstance(config['post'][key], dict):
                if key == 'creds': continue
                js += 'post_json.'+key+' = {\n'
                for sub_key in config['post'][key]:
                    js += '    "'+sub_key+'": '+str(config['post'][key][sub_key])+',\n'
                js += '}\n'
            elif isinstance(config['post'][key], list):
                js += 'post_json.'+key+' = "'+str(config['post'][key])+'";\n'
        js += '\n$http.post(\''+route.title+'\', post_json).success(function(data) {\n'
        js += '    if(data.'+config['route_success_flag']+' == true) {\n'
        for okey in output_response:
            if isinstance(output_response[okey], (basestring, int, bool, types.NoneType)):
                js += '        data.'+okey+'; // '+str(output_response[okey])+'\n'
            elif isinstance(output_response[okey], dict):
                js += '        data.'+okey+' = {\n'
                for sub_key in output_response[okey]:
                    js += '            "'+sub_key+'": '+str(output_response[okey][sub_key])+',\n'
                js += '        }\n'
            elif isinstance(output_response[okey], list):
                js += '        data.'+key+'; // '+str(config['post'][key])+'";\n'
        js += '    }\n'
        js += '})\n'
        js += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        route.sections[interface.EN_POST_RUNTIME] = js


    @classmethod
    def go_route(cls, route, config):
        route.status_stamp('FAIL', 1, datetime.datetime.now(), speed=0.0)
        path = cls.build_path(route.title, config)
        start_time = None
        result = {}
        if config.get('post'): # will return None if json has null for this key
            start_time = time.time()
            result = cls.POST(path, config['post'])
            speed = time.time() - start_time
        else:
            start_time = time.time()
            result = cls.GET(path)
            speed = time.time() - start_time
        return result, speed


    @classmethod
    def deal_with_output_response_data(cls, route, compatible, output_response, resp_instr):
        if resp_instr.get('max_list_print'):
            output_response = cls.trim_lists_in_json_struct(output_response, resp_instr.get('max_list_print'))
        if resp_instr.get('output'):
            route.sections[interface.RESPONSE] = json.dumps(output_response, indent=4, separators=(',', ': '))
            cls.log2(output_response)
        if resp_instr.get('write_to_predict_if_compatible'):
            if compatible:
                print 'OVER-WRITING PREDICT'
                route.sections[interface.PREDICT] = json.dumps(output_response, indent=4, separators=(',', ': '))


    @classmethod
    def run_route(cls, route, full_ch_config, full_ch_predict):
        full_config = copy.deepcopy(full_ch_config)
        route_config = json.loads(route.sections[interface.CONFIG])
        full_config = cls.merge_struct(full_config, route_config)
        full_config = cls.merge_struct(full_config, cls.runtime_config)

        full_predict = copy.deepcopy(full_ch_predict)
        route_predict = json.loads(route.sections[interface.PREDICT])
        full_predict = cls.merge_struct(full_predict, route_predict)
        full_predict = cls.merge_struct(full_predict, cls.runtime_predict)

        cls.log1(route, full_config, full_predict)

        result, speed_in_sec = cls.go_route(route, full_config)

        if result.status_code>=200 and result.status_code<300:
            route.status_stamp('START', 2, datetime.datetime.now(), speed=speed_in_sec)
        else:
            route.status_stamp('HTTP-'+str(result.status_code), 1, datetime.datetime.now(), speed=speed_in_sec)

        actual_response = result.json()
        output_response = copy.deepcopy(actual_response)

        if actual_response[full_config['route_success_flag']]:
            route.status_stamp('OKAYFLAG', 3, datetime.datetime.now(), speed=speed_in_sec) # keeping track of speed always...

        compatible = cls.is_compatible_json(actual_response, full_predict)
        if compatible:
            route.status_stamp('SUCCESS', 4, datetime.datetime.now(), speed=speed_in_sec)
        else:
            route.status_stamp('INCOMPAT', 2, datetime.datetime.now(), speed=speed_in_sec)

        # if we have been given instructions on what to do with the response data
        resp_instr = full_config.get('response')
        if resp_instr:
            cls.deal_with_output_resposne_data(output_response, resp_instr)
        else:
            print 'no response key in the config'

        cls.log3(route)
        cls.log_js_example(route, full_config, output_response)

        cls.runtime_config, cls.runtime_reply = route.runtime_exec(actual_response)

        return actual_response


    @classmethod
    def trim_lists_in_json_struct(cls, json_struct, length, counter=0):
        # print '~~~~~~~~~~~~~~~~ TRIM LISTS ~~~~~~~~~~~~~'+str(counter)
        # print 'type is: '+str(type(json_struct))
        # print json_struct
        if isinstance(json_struct, list):
            new_list = []
            for item in json_struct[:length]:
                trimmed_item = item
                if isinstance(item, (list, dict)):
                    trimmed_item = cls.trim_lists_in_json_struct(item, length, counter+1)
                new_list.append(trimmed_item)
            # print '~~~~~~ trimmed to list'+str(counter)
            # print new_list
            # print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'+str(counter)+'\n\n\n'
            return new_list
        elif isinstance(json_struct, dict):
            for key in json_struct:
                orig_value = json_struct[key]
                if isinstance(orig_value, (list, dict)):
                    # print 'value associated is either a list or a dict - attempting to trim'
                    trimmed_value = cls.trim_lists_in_json_struct(orig_value, length, counter+1)
                    json_struct[key] = trimmed_value
                else:
                    # print 'value associated is neither list nor dict - leaving it alone'
                    pass # leave the original value
            # print '~~~~~~ trimmed to dict'+str(counter)
            # print json_struct
            # print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'+str(counter)+'\n\n\n'
            return json_struct
        else:
            # print 'neither list nor dict'
            return json_struct




    @classmethod
    def is_compatible_json(cls, actual, predicted):

        # print 'being asked to compare json!'
        # print '\nactual'
        # print '------'
        # print actual
        # print '\npredicted'
        # print '-----------'
        # print predicted
        # print '==========================================\n\n'

        if isinstance(predicted, (basestring, bool, int, types.NoneType)):
            # print 'print testing basic'
            if cls.is_compatible_basic(actual, predicted):
                # print 'compatible json'
                return True
            else:
                # print 'incompatible json'
                return False
        elif isinstance(predicted, dict):
            # print 'print testing dict'
            if isinstance(actual, dict):
                if cls.is_compatible_dict(actual, predicted):
                    # print 'compatible dict'
                    return True
                else:
                    # print 'incompatible dict'
                    return False
            else:
                # print 'incompatible dict'
                return False
        elif isinstance(predicted, list):
            # print 'print testing list'
            if isinstance(actual, list):
                if cls.is_compatible_list(actual, predicted):
                    # print 'compatible list'
                    return True
                else:
                    # print 'incompatible list'
                    False
            else:
                # print 'incompatible list'
                return False

    @classmethod
    def is_compatible_list(cls, actual_list, predicted_list):
            if len(actual_list) < len(predicted_list):
                # print 'incompatible - actual list length less than predicted list length'
                return False
            else:
                for pr_item in predicted_list:
                    if not cls.is_in_actual_list(pr_item, actual_list):
                        # print 'incompatible - predicted item not found in actual list'
                        return False
                # print 'compatible list'
                return True

    @classmethod
    def is_in_actual_list(cls, pr_item, actual_list):
        for actual_item in actual_list:
            if cls.is_compatible_json(actual_item, pr_item):
                return True
        return False

    @classmethod
    def is_compatible_basic(cls, actual_basic, predicted_basic):
        if actual_basic == predicted_basic:
            # print 'compatible basic'
            return True
        else:
            # print 'incompatible - not equal'
            return False

    @classmethod
    def is_compatible_dict(cls, actual_dict, predicted_dict):
        for key in predicted_dict:
            if key not in actual_dict:
                # print 'incompatible - predicted key not in actual dict'
                return False
            else:
                compatible = cls.is_compatible_json(actual_dict[key], predicted_dict[key])
                if not compatible:
                    # print 'incompatible = key value in actual does not match key value in predicted'
                    return False
                else:
                    continue
        # print 'compatible dict'
        return True

    @classmethod
    def build_path(cls, route, config):
        cf_get = config.get('get')
        if cf_get is not None:
            for key in config.get('get'):
                route = route.replace(':'+key, config[key])
        return route


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
        print 'injecting: '+test_name
        setattr(cls, test_name, test_mthd)


    @classmethod
    def build_test_method(cls, chapter):
        chp = chapter
        def test_method(self):
            ch_config = json.loads(chp.sections[interface.JS_CONFIG])
            ch_reply  = json.loads(chp.sections[interface.JS_REPLY])
            Ddd_TestCase.run_route_list(chp.route_list, ch_config, ch_reply)

        return test_method


default_base_url='http://216.224.141.220:5438'
default_http_headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
def init_DocDrivenTestCase(driven_down_doc, base_url=default_base_url, http_headers=default_http_headers):

    # REMOVE TEST CASES FROM LAST TIME -- EACH INIT SHOULD BE FRESH

    DocDrivenTestCase.driven_down_doc = driven_down_doc
    DocDrivenTestCase.default_base_url = base_url
    DocDrivenTestCase.default_http_headers = http_headers

    # we dont want a class with no tests, because then
    # the introduction/conclusion won't get run
    def empty_test(self):
        pass
    setattr(DocDrivenTestCase, 'test_empty', empty_test)

    # we add one test method per chapter
    for chapter in DocDrivenTestCase.driven_down_doc.chapter_list:
        DocDrivenTestCase.insert_test_method(chapter)

    return DocDrivenTestCase




