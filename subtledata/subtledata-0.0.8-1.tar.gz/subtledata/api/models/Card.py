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
class Card:
    """NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually."""


    def __init__(self):
        self.swaggerTypes = {
            'name_on_card': 'str',
            'card_type': 'str',
            'expiration_year': 'str',
            'card_id': 'int',
            'expiration_month': 'str',
            'nickname': 'str',
            'last_4_digits': 'str'

        }


        #Name on card
        self.name_on_card = None # str
        #Card type
        self.card_type = None # str
        #Year of card expiration date (4 digits)
        self.expiration_year = None # str
        #SubtleData Card ID
        self.card_id = None # int
        #Month of card expiration date (2 digits)
        self.expiration_month = None # str
        #Card nickname
        self.nickname = None # str
        #Last 4 digits on card
        self.last_4_digits = None # str
        
