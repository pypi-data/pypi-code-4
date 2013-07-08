'''
Created on Apr 30, 2013

:author: chen
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
