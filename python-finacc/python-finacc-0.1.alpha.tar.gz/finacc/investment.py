__author__ = 'samiths'


def rate_of_inflation(initial_cpi, ending_cpi):
    return (ending_cpi-initial_cpi)/initial_cpi


def real_rate_of_return(nominal_rate, inflation_rate):
    return ((1+nominal_rate)/(1+inflation_rate))-1
