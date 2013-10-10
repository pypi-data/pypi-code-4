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

import requests

def parse():
    """
    @summary:接收参数，负责功能调用。
    """
    if len( sys.argv ) == 2:
        if sys.argv[1] == 'title':
            print "Mpis_ID 节点名称 节点编号 出口交换机管理IP 核心交换机管理IP 管理服务器IP PDN内网IP TTA服务-ETH0 TTA服务-ETH1 FC服务-ETH0 FC服务-ETH1 测试设备-ETH0 测试设备-ETH1 备注 IPMI"
            print url_get( "device" )
        elif sys.argv[1] == 'device':
            print url_get('device')
        elif sys.argv[1] == 'host':
            print url_get('host')
    else:
        print "\nUsage: " + sys.argv[0]
        print "+---------------------------------------------------+"
        print "| example 1: "  + sys.argv[0] + " title"
        print "| example 2: "  + sys.argv[0]
        print "+---------------------------------------------------+\n"
        exit(1)

def url_get( order ):
    """
    -- 小写 no"-"
    eg: device_info_test.py--url http://192.168.137.76:8000/
    """
    url = "http://223.203.188.114:9011/api/" + order + "/"
    #url = "http://127.0.0.1:8000/api/host/"
    hyper_text = requests.get( url )
    if hyper_text.status_code != 200:
        exit(1)
    return hyper_text.text
if __name__ == "__main__":
    parse()
