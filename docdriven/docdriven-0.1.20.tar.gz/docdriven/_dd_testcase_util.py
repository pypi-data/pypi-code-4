import re
import requests
import json
import datetime
import interface
import types
import logging
import time
import pprint

import testcase

log = logging.getLogger(__name__)


def get(path, base_url, http_headers):
    print '\nHITTING ROUTE: '+path
    return requests.get(base_url+path, headers=http_headers)

def post(path, data, base_url, http_headers):
    if not isinstance(data, str):
        data = json.dumps(data)
    print '\nHITTING ROUTE: '+path
    return requests.post(base_url+path, data=data, headers=http_headers)

def go_route(route, config):
    route.report_stamp('FAIL', 1, datetime.datetime.now(), speed=0.0)
    path = build_path(route.title, config)
    start_time = None
    result = {}
    if config.get('http_post'): # will return None if json has null for this key
        log.debug('POST - '+path)
        start_time = time.time()
        result = post(path, config['http_post'], testcase.default_base_url, testcase.default_http_headers)
        speed = time.time() - start_time
    else:
        log.debug('GET  - '+path)
        start_time = time.time()
        result = get(path, testcase.default_base_url, testcase.default_http_headers)
        speed = time.time() - start_time
    return result, speed

def merge_struct(base, local):
    if base is None:
        return local  # so in the case that local is None, we return None
    if isinstance(base, dict) and isinstance(local, dict):
        for key in local:
            if not key in base:
                base[key] = local[key]
            else:
                if isinstance(local[key], dict):
                    base[key] = merge_struct(base[key], local[key])
                else:
                    base[key] = local[key]
        return base
    elif isinstance(base, list) and isinstance(local, list):
        # if we are trying to merge two lists then we want every item in the local
        # list to appear in the base list.  If an item is not in the base list, we
        # will add it.  We check if an item is in the base list by checking for
        # compatibility.
        for item in local:
            if not is_in_list(base):  # this will check for compatible json
                base.append(item)
        return base
    else:
        return local
        # raise Exception('Cannot merge unless base and local have the same type (which must be dict or list)')

def log1(route, config, predict):
    log_string = ''
    log_string += '=========================================================================================\n'
    log_string += 'running route: '+route.title+' '+datetime.datetime.now().isoformat()[11:19]+'\n'
    log_string += '=========================================================================================\n'
    log_string += '#### config\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
    log_string += json.dumps(config, indent=4, separators=(',', ': '))+'\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    log_string += '#### predict\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
    log_string += json.dumps(predict, indent=4, separators=(',', ': '))+'\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    return ''#log_string

def log2(route):
    log_string = ''
    log_string += '#### response\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
    log_string += json.dumps(route.get_json_section(interface.RESPONSE), indent=4, separators=(',', ': '))+'\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    return ''#log_string

def log3(route):
    log_string = '#### report\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
    log_string += json.dumps(route.get_json_section(interface.REPORT), indent=4, separators=(',', ': '))+'\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    log_string += '#### python\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  python\n'
    log_string += route.sections[interface.RUNTIME]+'\n'
    log_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    return ''#log_string

def log_js_example(route, config, output_response):
    js = '\n**JAVASCRIPT**\n'
    js += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  javascript\n'
    js += 'post_json = {}\n'
    for key in config['http_post']:
        if isinstance(config['http_post'][key], (basestring, int, bool, types.NoneType)):
            js += 'post_json.'+key+' = "'+str(config['http_post'][key])+'";\n'
        elif isinstance(config['http_post'][key], dict):
            if key == 'creds': continue
            js += 'post_json.'+key+' = {\n'
            for sub_key in config['http_post'][key]:
                js += '    "'+sub_key+'": '+str(config['http_post'][key][sub_key])+',\n'
            js += '}\n'
        elif isinstance(config['http_post'][key], list):
            js += 'post_json.'+key+' = "'+str(config['http_post'][key])+'";\n'
    js += '\n$http.post(\''+route.title+'\', post_json).success(function(data) {\n'
    if config.get('route_success_flag'):
        js += '    if(data.'+config['route_success_flag']+' == true) {\n'
    else:
        js += '    if (data) {      // no route_success_flag\n'

    if type(output_response) == dict:
        for okey in output_response:
            if isinstance(output_response[okey], (basestring, int, bool, types.NoneType)):
                js += '        data.'+okey+'; // '+str(output_response[okey])+'\n'
            elif isinstance(output_response[okey], dict):
                js += '        data.'+okey+' = {\n'
                for sub_key in output_response[okey]:
                    js += '            "'+sub_key+'": '+str(output_response[okey][sub_key])+',\n'
                js += '        }\n'
            elif isinstance(output_response[okey], list):
                js += '        data.'+okey+'; // '+str(output_response[okey])+'";\n'
    js += '    }\n'
    js += '})\n'
    js += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
    # route.sections[interface.POST_RUNTIME] = js
    route.sections[interface.POST_RUNTIME] = ''

def trim_lists_in_json_struct(json_struct, length, counter=0):
    if isinstance(json_struct, list):
        new_list = []
        for item in json_struct[:length]:
            trimmed_item = item
            if isinstance(item, (list, dict)):
                trimmed_item = trim_lists_in_json_struct(item, length, counter+1)
            new_list.append(trimmed_item)
        return new_list
    elif isinstance(json_struct, dict):
        for key in json_struct:
            orig_value = json_struct[key]
            if isinstance(orig_value, (list, dict)):
                # log.debug('value associated is either a list or a dict - attempting to trim')
                trimmed_value = trim_lists_in_json_struct(orig_value, length, counter+1)
                json_struct[key] = trimmed_value
            else:
                pass # leave the original value
        return json_struct
    else:
        return json_struct

def is_compatible_json(actual, predicted):
    if isinstance(predicted, (basestring, bool, int, types.NoneType)):
        return (actual == predicted)
    elif isinstance(predicted, dict):
        if isinstance(actual, dict):
            return is_compatible_dict(actual, predicted)
        else:
            return False
    elif isinstance(predicted, list):
        if isinstance(actual, list):
            return is_compatible_list(actual, predicted)
        else:
            return False

def is_compatible_list(actual_list, predicted_list):
    if len(actual_list) < len(predicted_list):
        return False
    else:
        for pr_item in predicted_list:
            if not is_in_list(pr_item, actual_list):
                return False
        return True

def is_in_list(pr_item, given_list):
    for item in given_list:
        if is_compatible_json(item, pr_item):
            return True
    return False


def is_compatible_dict(actual_dict, predicted_dict):
    for key in predicted_dict:
        if key not in actual_dict:
            return False
        else:
            compatible = is_compatible_json(actual_dict[key], predicted_dict[key])
            if not compatible:
                return False
            else:
                continue  # keep checking the rest of the keys
    return True  # we checked them all without return false, so we're good

def build_path(route, config):
    cf_get = config.get('http_get')
    if cf_get is not None:
        for key in config.get('http_get'):
            route = route.replace(':'+key, str(config['http_get'][key]))
    return route

def deal_with_output_response_data(route, compatible, output_response, resp_instr, log_string):
    if resp_instr.get('max_list_print'):
        output_response = trim_lists_in_json_struct(output_response, resp_instr.get('max_list_print'))
    if resp_instr.get('output'):
        route.put_json_section(interface.RESPONSE, output_response)
        log_string += log2(route)
    if resp_instr.get('write_to_predict_if_compatible'):
        if compatible:
            log.debug('OVER-WRITING PREDICT')
            route.put_json_section(interface.PREDICT, output_response)
    return log_string

