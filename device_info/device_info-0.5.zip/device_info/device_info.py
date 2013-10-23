#! /home/web/envs/web/bin/python
#-*- coding: utf-8 -*-
'''
Created on 2013-09-23
@author: happyguannan@gmail.com
@summary: device info
@version: 0.1
'''

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from optparse import OptionParser
import requests

parser = OptionParser("device_info.py device [-t --title]|host [-t --title]|server [-n --name <typename>][-s --server <style>]")
parser.add_option("-n", "--num", dest="node_num",
                  help="参数为节点编号", metavar="NUM")
parser.add_option("-s", "--service", dest="service",
                  help="服务类型(选项为:'tta'或‘fc’或'pis'或‘tst’)", metavar="SERVICE")
parser.add_option("-t", "--title",
                  action="store_true", default=False, help="device -t or host -t")
options, args = parser.parse_args()


def parse():
    """
    @summary:接收参数，负责功能调用。
    """
    available_args = ["device", "host", "server"]
    if options.service and options.node_num:
        if len(args) == 1 and args[0] == "server":
            print url_get(
                "server/?num=%s&ser=%s" % (options.node_num, options.service))
        else:
            print "无效的参数 正确形式:server -n CNC-BI-1 -s TTA"
    elif options.node_num:
        if len(args) == 1 and args[0] == "server":
            print url_get("server/?num=%s" % (options.node_num))
        else:
            print "无效的参数 正确形式:server -n CNC-BI-1"

    elif options.service:
        if len(args) == 1 and args[0] == "server":
            print url_get("server/?ser=%s" % (options.service))
        else:
            print "无效的参数 正确形式:server -s TTA"

    elif len(args) == 1 and bool((set(args) & set(available_args))):
        if args[0] == "server":
            print "请传入参数 [-n --name <typename>][-s --server <style>]"
        print url_get(args[0] + "/" + "?title=%s" % str(bool(options.title)))

    else:
        print parser.print_help()


def url_get( order ):
    """
    -- 小写 no"-"
    eg: device_info.py--url http://192.168.137.76:8000/
    """
    url = "http://223.203.188.114/api/" + order
    # url = "http://127.0.0.1:8080/api/" + order
    hyper_text = requests.get(url)
    if hyper_text.status_code != 200:
        exit(1)
    return hyper_text.text


if __name__ == "__main__":
    parse()
