'''
Copyright 2013-2013 Chen Huang.
All rights reserved. FreeBSD License.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the
     distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from talib.abstract import Function
import pandas as pd
import numpy as np


class TAIndicator(Function):
    '''
    Indicator subclass tablib function class and make it compatible with pandas data frame by overloading set_input_arrays
    '''

    def __init__(self, function_name, *args, **kwargs):
        '''
        Constructor
        '''
        Function.__init__(self, function_name, args, kwargs)

    def set_input_arrays(self, input_data):
        '''
        Recalculate new Indicator
        '''
        if Function.set_input_arrays(self, input_data):
            return True
        elif isinstance(input_data, pd.DataFrame):
            input_arrays = {}
            for tag, column in input_data.iteritems():
                input_arrays[tag] = np.asarray(column)
            # convert input_data to input_arrays and then call the super
            Function.set_input_arrays(self, input_arrays)
            return True
        return False

    def get_input_arrays(self):
        """
        Returns a copy of pandas data frame
        """
        return self.__input_arrays.copy()
