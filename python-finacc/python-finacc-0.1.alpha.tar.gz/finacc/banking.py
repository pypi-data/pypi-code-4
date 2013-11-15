__author__ = 'samiths'

from math import pow, e


def annual_percentage_yield(r, n):
    return pow(1+(r/n), n)-1


def loan_balloon_payment(pv, bamt, r, n):
    return (pv-(bamt/pow(1+r, n)))*(r/(1-pow(1+r, n*-1)))


def loan_balloon_balance(pv, p, r, n):
    return (pv*pow(1+r, n))-(p*((pow(1+r, n)-1)/r))


def loan_payment(pv, r, n):
    return (r*pv)/(1-pow(1+r, n*-1))


def loan_remaining_balance(pv, p, r, n):
    return (pv*pow(1+r, n))-(p*((pow(1+r, n)-1)/r))


def loan_to_deposit_ratio(loans, deposits):
    return loans/deposits


def loan_to_value_ratio(loan, value):
    return loan/value


def simple_interest(p, r, t):
    return p*r*t


def ending_balance_for_simple_interest(p, r, t):
    return p*(1+(r*t))


def compound_interest(p, r, n):
    return p*(pow(1+r, n)-1)


def continuous_compounding(p, r, t):
    return p*pow(e, r*t)


def dept_to_income_ratio(debt, income):
    return debt/income
