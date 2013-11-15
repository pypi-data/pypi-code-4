#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

""" how to encode a (username, password) pair. See also schema example. """

from formv.validators.encoders import VEncodedPair

def encode_password():
    u = 'dummy@dummy.com'; p = 'dummy-secret-password'  
    value = {'username':u, 'password':p}          
    return VEncodedPair(required_field='password', 
                        required_label='Password', 
                        available_field='username').validate(value)

if __name__=='__main__':
    print(encode_password())