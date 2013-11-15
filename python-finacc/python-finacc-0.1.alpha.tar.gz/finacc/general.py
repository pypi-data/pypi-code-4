__author__ = 'samiths'

from math import pow, e


def future_value_of_annuity(p, r, n):
    return p*((pow(1+r, n)-1)/r)


def fv_of_annuity_continuous_compounding(cf, r, t):
    return cf*((pow(e, r*t)-1)/(pow(e, r)-1))

