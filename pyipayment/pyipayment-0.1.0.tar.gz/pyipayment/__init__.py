import base64
import urllib
from urllib2 import HTTPError
from urlparse import urlparse, parse_qs

import json
import logging
import sys
import mechanize
from bs4 import BeautifulSoup
from decimal import *
from datetime import *

"""
Steps to use this API:

"""

log = logging.getLogger(__name__)

class IPaymentException(Exception):
    pass

class IPaymentAPI(object):

    def __init__(self, username, password):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout)
        log.debug("Initializing IPaymentAPI class.")

        self.username = username
        self.password = password
        self.mech = mechanize.Browser(factory=mechanize.DefaultFactory(i_want_broken_xhtml_support=True))
        self.mech.set_handle_robots(False)
        self.mech.set_debug_http(False)
        self.mech.addheaders = [('User-agent', 'User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0')]

    def login(self):

        try:
          url = "https://iaccess.merchant-info.com/Login.aspx"
          log.debug("Opening URL %s" % url)
          response = self.mech.open(url)
        except HTTPError, e:
          sys.exit("%d: %s" % (e.code, e.msg))

        # Select the form, fill the fields, and submit
        self.mech.select_form(nr=0)
        self.mech["ctl00$ContentPlaceHolder1$Login1$UserName"] = self.username
        self.mech["ctl00$ContentPlaceHolder1$Login1$Password"] = self.password
        try:
          response = self.mech.submit()
        except HTTPError, e:
          sys.exit("Login failed: %d: %s" % (e.code, e.msg))


    def batch_details(self, start_date, end_date):
        """ Retrieves the batch details for a specific day. """

        # Select the form, fill the fields, and submit
        self.mech.select_form(nr=0)
        self.mech["ctl00$cph$drp$txtFromDate"] = start_date.strftime('%m/%d/%Y')
        self.mech["ctl00$cph$drp$txtToDate"] = end_date.strftime('%m/%d/%Y')
        try:
          response = self.mech.submit()
        except HTTPError, e:
          sys.exit("Unable to retrieve batch details: %d: %s" % (e.code, e.msg))


        html = response.read()

        net_processing_data = self.parse_net_processing(html)
        return net_processing_data


    def parse_net_processing(self, html):
        net_processing_data = []

        soup = BeautifulSoup(html)
        table = soup.find_all('table','mpLeft')

        if len(table) <= 0:
            return net_processing_data

        soup = BeautifulSoup( str(table[0]) )

        for row in soup.find_all('tr')[3:-1]:
            cells = BeautifulSoup(str(row)).find_all('td')


            cells = map(lambda x: x.text.strip().replace('$', '').replace(',', ''), cells)

            settlement_date = datetime.strptime(cells[0],"%m/%d/%Y").date()
            sale_count = int(cells[1])
            sale_amount = Decimal(cells[2])
            return_count = int(cells[3])
            return_amount = Decimal(cells[4])
            discount = Decimal(cells[5])
            net_amount = Decimal(cells[6])

            net_processing_data.append({
                'settlement_date' : settlement_date,
                'sale_count' : sale_count,
                'sale_amount' : sale_amount,
                'return_count' : return_count,
                'return_amount' : return_amount,
                'discount' : discount,
                'net_amount' : net_amount
            })
        return net_processing_data
