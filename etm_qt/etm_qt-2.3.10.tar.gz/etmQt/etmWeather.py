# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import platform
if platform.python_version() >= '3':
    python_version2 = False
    from urllib import request as Request
    from urllib.request import urlopen
    from urllib.error import URLError
    from urllib.parse import urlencode
    from io import StringIO
    from html.parser import HTMLParser
    import pickle
    unicode = str
    u = lambda x: x
else:
    # print('using python 2')
    python_version2 = True
    from urllib2 import Request, urlopen, URLError
    from cStringIO import StringIO
    import cPickle as pickle
    QString = lambda x: x
    from urllib import urlencode
    from HTMLParser import HTMLParser

from xml.etree.ElementTree import ElementTree, tostring
import socket
import re
from locale import getdefaultlocale
from textwrap import wrap as text_wrap


from datetime import datetime
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QObject

import codecs
encoding = codecs.lookup('utf-8').name

today = datetime.now()

lcl = getdefaultlocale()

city = state = place = ""
lat = lon = []

s_regex = re.compile(' ', re.M | re.L | re.U)
y_regex = re.compile(r'\{.*\}units$')


def tr(string):
    return(str(QApplication.translate('etmWeather', string)))


class Weather(QObject):

    def __init__(self, location):
        QObject.__init__(self)
        self.weather_location = str(location)

    def direction(self, deg):
        points = [
            self.tr('N'),
            self.tr('NNE'),
            self.tr('NE'),
            self.tr('ENE'),
            self.tr('E'),
            self.tr('ESE'),
            self.tr('SE'),
            self.tr('SSE'),
            self.tr('S'),
            self.tr('SSW'),
            self.tr('SW'),
            self.tr('WSW'),
            self.tr('W'),
            self.tr('WNW'),
            self.tr('NW'),
            self.tr('NNW')]

        index = (int(deg) * 100 + 1125) // 2250
        if index == 16:
            return points[0]
        else:
            return points[index]

    def getWeather(self):
        ret = []
        frcst = []
        timeout = 10
        socket.setdefaulttimeout(timeout)
        if not (self.weather_location.startswith('p=') or
                self.weather_location.startswith('w=')):
            # assume p=
            self.weather_location = "p={0}".format(self.weather_location)
        url = 'http://xml.weather.yahoo.com/forecastrss?{0}'.format(
            self.weather_location)
        try:
            response = urlopen(url)
        except URLError as e:
            if hasattr(e, 'reason'):
                msg = """\
    We failed to reach the weather server at
        %s
    Reason: %s.""" % (url, e.reason)
            elif hasattr(e, 'code'):
                msg = """\
    The weather server at
        %s
    couldn\'t fulfill the request.
    Error code: %s.""" % (url, e.code)
            return(0, msg)

        # connection is fine
        tree = ElementTree()
        response = urlopen(url)
        tree.parse(response)
        channel = tree.find("channel")
        data = {}
        if not channel is None:
            elements = channel.getchildren()
            for element in elements:
                if not element is None:
                    m = y_regex.match(element.tag)
                    if m:
                        group = 'units:'
                    else:
                        group = ''
                    items = element.items()
                    for item in items:
                        if item[0] in [
                                'city', 'region', 'country',
                                'temperature', 'distance', 'pressure', 'speed',
                                'direction', 'chill', 'pressure', 'rising',
                                'visibility', 'humidity', 'sunrise', 'sunset']:
                            data["%s%s" % (group, item[0])] = item[1]
        title = "%s %s" % ("weather", data['city'])
        if data['region']:
            title += ", %s" % data['region']
        elif data['country']:
            title += ", %s" % data['country']
        channelitem = channel.find("item")
        if channelitem is not None:
            elements = channelitem.getchildren()
            first = True
            second = False
            temperature = 0
            for element in elements:
                if element is not None:
                    items = element.items()
                    hash = {}
                    string = ""
                    for item in items:
                        if item[0] in [
                                'day', 'date', 'text', 'temp', 'high', 'low']:
                            hash[item[0]] = item[1]
                            if item[0] == 'temp':
                                temperature = item[1]
                    if hash:
                        if first:
                            ret.append(title)
                            ret.append(
                                "    %s: %s" %
                                (self.tr("current conditions"), hash['date']))
                            keys = ['text', 'temp']
                            first = False
                            second = True
                        elif second:
                            keys = ['day', 'date', 'text', 'temp']
                            string = "        %s " % self.tr("wind")
                            if data['speed'] and float(data['speed']) > 0:
                                for key in ['direction', 'speed', 'chill']:
                                    if key in data:
                                        if key == 'direction':
                                            string += "%s, " % (
                                                self.direction(data[key]))
                                        elif key == 'chill' and \
                                                data['chill'] != temperature:
                                            string += ", %s %s%s" % (
                                                self.tr('feels like'),
                                                data['chill'],
                                                data['units:temperature'])
                                        elif key == 'speed':
                                            string += "%s %s %s" % (
                                                self.tr("speed"),
                                                data[key],
                                                data['units:speed'])
                            else:
                                string += self.tr("calm")
                            ret.append(string)
                            string = "        "
                            for key in [
                                    'humidity', 'visibility',
                                    'pressure', 'rising']:
                                if key in data:
                                    if key == 'pressure':
                                        string += "%s %s %s, " % (
                                            self.tr("pressure"),
                                            data[key],
                                            data['units:pressure'])
                                    elif key == 'visibility':
                                        string += "%s %s %s, " % (
                                            self.tr("visibility"),
                                            data[key],
                                            data['units:distance'])
                                    elif key == 'rising':
                                        if data['rising'] == '1':
                                            string += self.tr("rising")
                                        elif data['rising'] == '-1':
                                            string += self.tr("falling")
                                        else:
                                            string += self.tr("constant")
                                    elif key == "humidity":
                                        string += "%s %s, " % (
                                            self.tr("humidity"),
                                            data[key])
                            ret.append(string)
                            string = "        "
                            for key in ['sunrise', 'sunset']:
                                if key in data:
                                    if key == 'sunrise':
                                        string += "%s %s, " % (
                                            self.tr('sunrise'),
                                            data[key])
                                    else:
                                        string += "%s %s" % (
                                            self.tr('sunset'),
                                            data[key])
                            ret.append(string)
                            #### Forecast ####
                            ret.append("    %s" % self.tr("forecast"))
                            second = False
                        string = "        "
                        fst = ""
                        for key in keys:
                            if key in hash:
                                if key == 'day':
                                    string += "%s, " % hash[key]
                                elif key == 'date':
                                    string += "%s: " % hash[key]
                                elif key == 'temp':
                                    string += "%s%s" % (
                                        hash[key], data['units:temperature'])
                                    fst += "%s%s" % (
                                        hash[key], data['units:temperature'])
                                else:
                                    string += "%s, " % hash[key]
                                    fst += "%s, " % hash[key]
                        for key in ['high', 'low']:
                            if key in hash:
                                if key == 'high':
                                    string += "%s %s%s, " % (
                                        self.tr('high'),
                                        hash[key],
                                        data['units:temperature'])
                                    fst += "%s %s%s, " % (
                                        self.tr('high'),
                                        hash[key],
                                        data['units:temperature'])
                                elif key == 'low':
                                    string += "%s %s%s" % (
                                        self.tr('low'),
                                        hash[key],
                                        data['units:temperature'])
                                    fst += "%s %s%s" % (
                                        self.tr('low'),
                                        hash[key],
                                        data['units:temperature'])
                        ret.append(string)
                        frcst.append(fst)
        return(1, ret)

    def getForecast(self):
        f = []
        ok, l = self.getWeather()
        if ok:
            f.append(l[1].strip().split('s: ')[1])
            f.append(l[2].strip())
            for i in [-2, -1]:
                f.append(l[i].split(':')[1].strip())
        else:
            f = l
        return(ok, f)


class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.capture = False
        self.pre = False
        self.more = True
        self.output = []
        self.para = ''
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ['p', 'pre']:
            if tag == 'pre':
                self.pre = True
            self.capture = True
        elif tag == "strong":
            self.output.append('')
        elif tag in ['hr', 'a']:
            self.more = False

    def handle_endtag(self, tag):
        if tag in ['p', 'pre']:
            if tag == 'pre':
                self.pre = False
                self.output.append('')
            else:

                l = text_wrap(self.para, width=70)
                self.output.extend(l)
                self.output.append('')
                self.para = ''
            self.capture = False

    def handle_data(self, text):
        if self.more and self.capture:
            if self.pre:
                text = text.rstrip()
                if text:
                    self.skip = False
                    out = []
                    parts = text.split('\n')
                    for part in parts:
                        p = part.rstrip()
                        if p:
                            self.output.append("%s\n" % p)
                else:
                    self.skip = True
            else:
                l = text.split()
                self.para += " ".join(l)

    def output(self):
        return self.output


def getSunMoon(loc=None, d=None):
    sunmoon_location = loc
    import socket
    timeout = 10
    socket.setdefaulttimeout(timeout)
    data = {}
    sunmoon_location = loc
    if len(sunmoon_location) == 2:
        ffx = 1
        data['place'] = sunmoon_location[0]
        data['st'] = sunmoon_location[1]
    elif len(sunmoon_location) == 7:
        ffx = 2
        data['place'] = sunmoon_location[0]
        if sunmoon_location[1].upper() == 'E':
            data['xx0'] = 1
        elif sunmoon_location[1].upper() == 'W':
            data['xx0'] = -1
        data['xx1'] = sunmoon_location[2]
        data['xx2'] = sunmoon_location[3]

        if sunmoon_location[4].upper() == 'N':
            data['yy0'] = 1
        elif sunmoon_location[4].upper() == 'S':
            data['yy0'] = -1
        data['yy1'] = sunmoon_location[5]
        data['yy2'] = sunmoon_location[6]

        if time.localtime().tm_isdst:
            utcoffset = time.altzone/3600
        else:
            utcoffset = time.timezone/3600
        if utcoffset < 0:
            # east of Greenwich
            data['zz0'] = 1
            data['zz1'] = -utcoffset
        else:
            # west of Greenwich
            data['zz0'] = -1
            data['zz1'] = utcoffset
    else:
        return (0, """\
There is a problem with the setting for \'sunmoon_location\' in ~/.etmrc.""")

    if d:
        year, month, day = duparse(d).strftime("%Y %m %d").split()
    else:
        year, month, day = datetime.now().strftime("%Y %m %d").split()

    # this hack is needed to put FFX and xxy first - otherwise usno uses
    # latitude degrees as the year.
    url_data = "FFX=%s&xxy=%s&xxm=%s&xxd=%s&" % (ffx, year, month, day)
    url_data += urlencode(data)
    url = 'http://aa.usno.navy.mil/cgi-bin/aa_pap.pl'
    # req = Request(url)
    try:
        if python_version2:
            response = urlopen(url, url_data)
        else:
            response = urlopen(url, bytes(url_data, encoding))
    except URLError as e:
        if hasattr(e, 'reason'):
            msg = """\
We failed to reach a server.
Reason: %s.""" % e.reason
        elif hasattr(e, 'code'):
            msg = """\
The server couldn\'t fulfill the request.
Error code: %s.""" % e.code
        return(0, msg)
    # connection is fine
    data = response.read().decode(encoding)
    data = s_regex.sub('.', data)
    myparser = MyHTMLParser()
    myparser.feed(data)
    myparser.close()
    return(0, '\n'.join([x.rstrip() for x in myparser.output]))

if __name__ == "__main__":
    import sys
    sunmoon_location = ['Chapel Hill', 'NC']
    weather_location = 'USNC0105&u=f'  # Chapel Hill
    print("------------------ getWeather ---------------------")
    myweather = Weather(weather_location)
    ok, l = myweather.getWeather()
    if ok:
        print("\n".join(l))
    else:
        print(l)

    print("\n------------------- getSunMoon -------------------")
    ok, l = getSunMoon(sunmoon_location)
    if ok:
        print("\n".join(l))
    else:
        print(l)
