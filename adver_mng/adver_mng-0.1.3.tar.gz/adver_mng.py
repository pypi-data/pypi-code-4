#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = (0, 1, 3)

import datetime
import re
from flask import current_app, request
import functools

#投放广告的时间段
ADVER_HOURS = range(0, 9) + range(22, 24)

#广告IP屏蔽
ADVER_DENY_IP_PATTERN = r'113\.108\.76\.|183\.60\.52\.184'

# user agent 屏蔽
ADVER_DENY_USER_AGENT_PATTERN = r'python|curl'


def catch_execption(func):
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
        except Exception, e:
            return -100, __import__('traceback').format_exc()
        else:
            return r

    return func_wrapper


class AdverMng(object):
    """
    还是用类的方式好一些
    """

    _adver_hours = ADVER_HOURS
    _adver_deny_ip_pattern = ADVER_DENY_IP_PATTERN

    def __init__(self, adver_hours=None, adver_deny_ip_pattern=None):
        super(AdverMng, self).__init__()

        if adver_hours is not None:
            self._adver_hours = adver_hours

        if adver_deny_ip_pattern is not None:
            self._adver_deny_ip_pattern = adver_deny_ip_pattern

    @catch_execption
    def check(self, request):
        """
        判断是否禁止显示广告
        返回: ret, msg
        ret:
            0   代表允许
            1   代表属于正常过滤
            <0  代表非正常过滤，要打印内容
        """

        now_hour = datetime.datetime.now().hour

        if now_hour not in self._adver_hours:
            return 1, 'not in right time'

        userip = ''
        user_agent = ''
        connection = ''

        headers = dict()

        if hasattr(request, 'remote_addr'):
            # 说明是flask的请求
            userip = request.remote_addr
            headers = request.headers
            if 'User-Agent' in headers:
                user_agent = headers['User-Agent'].strip()
            if 'Connection' in headers:
                connection= headers['Connection'].strip()
        elif hasattr(request, 'META'):
            # django 的球球
            userip = request.META.get('REMOTE_ADDR', '')
            headers = request.META
            if 'HTTP_USER_AGENT' in headers:
                user_agent = headers['HTTP_USER_AGENT'].strip()
            if 'HTTP_CONNECTION' in headers:
                connection = headers['HTTP_CONNECTION'].strip()

        #print userip, '|', user_agent, '|', accept

        if re.match(self._adver_deny_ip_pattern, userip):
            # 如果匹配了ip
            return -1, '%s is forbid to show adver, headers:%s' % (userip, str(headers))

        re_user_agent = re.compile(ADVER_DENY_USER_AGENT_PATTERN, re.I)
        if user_agent == '' or re_user_agent.search(user_agent):
            return -2, '%s is forbid to show adver, headers:%s' % (userip, str(headers))

        re_connection = re.compile(r'keep-alive', re.I)
        if not re_connection.search(connection):
            return -3, '%s is forbid to show adver, headers:%s' % (userip, str(headers))

        return 0, '%s is allow to show adver, headers:%s' % (userip, str(headers))

