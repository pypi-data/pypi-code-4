#!/usr/bin/env python
"""
Copyright 2012 Wordnik, Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
class NewLocationStatus:
    """NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually."""


    def __init__(self):
        self.swaggerTypes = {
            'cross_streets': 'str',
            'receipt_number_instructions': 'str',
            'employee_request_through_app': 'bool',
            'menu_ordering_available': 'bool',
            'payment_via_credit_card_available_message': 'str',
            'postal_code': 'str',
            'location_id': 'int',
            'app_specials': 'bool',
            'user_rating': 'str',
            'location_name': 'str',
            'tender_types': 'list[TenderType]',
            'process_new_credit_cards': 'bool',
            'table_number_instructions': 'str',
            'state': 'str',
            'color_theme': 'int',
            'latitude': 'float',
            'logo_url': 'str',
            'website_url': 'str',
            'revenue_centers': 'list[RevenueCenter]',
            'city': 'str',
            'ordering_available_message': 'str',
            'phone': 'str',
            'terminals': 'list[Terminal]',
            'location_picture_url': 'str',
            'favorites_ordering_available': 'bool',
            'neighborhood_name': 'str',
            'discount_types': 'list[DiscountType]',
            'longitude': 'float',
            'price_rating': 'int',
            'process_pre_authed_cards': 'bool',
            'address_line_2': 'str',
            'address_line_1': 'str'

        }


        #Cross Streets
        self.cross_streets = None # str
        #Receipt number instructions
        self.receipt_number_instructions = None # str
        #Request for help throguh the app
        self.employee_request_through_app = None # bool
        #Menu Available
        self.menu_ordering_available = None # bool
        #Payment via credit card available message
        self.payment_via_credit_card_available_message = None # str
        #Address Postal Code
        self.postal_code = None # str
        #Location ID
        self.location_id = None # int
        #Specials available through app
        self.app_specials = None # bool
        #User Rating
        self.user_rating = None # str
        #Location Name
        self.location_name = None # str
        self.tender_types = None # list[TenderType]
        #Process New Credit Cards
        self.process_new_credit_cards = None # bool
        #Table number instructions
        self.table_number_instructions = None # str
        #Address State
        self.state = None # str
        #Color Theme
        self.color_theme = None # int
        #Location Latitude
        self.latitude = None # float
        #Logo URL
        self.logo_url = None # str
        #Website URL
        self.website_url = None # str
        self.revenue_centers = None # list[RevenueCenter]
        #Address City
        self.city = None # str
        #Ordering available message
        self.ordering_available_message = None # str
        #Phone Number
        self.phone = None # str
        self.terminals = None # list[Terminal]
        #Location Picture URL
        self.location_picture_url = None # str
        #Favorites available for ordering
        self.favorites_ordering_available = None # bool
        #Neighborhood Name
        self.neighborhood_name = None # str
        self.discount_types = None # list[DiscountType]
        #Location Longitude
        self.longitude = None # float
        #Price Rating
        self.price_rating = None # int
        #Process Pre Authed Credit Cards
        self.process_pre_authed_cards = None # bool
        #Address Line 2
        self.address_line_2 = None # str
        #Address Line 1
        self.address_line_1 = None # str
        
