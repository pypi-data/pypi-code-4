"""Validate and format Australian Business Numbers (ABNs)."""

import copy
import operator

ABN_MAX_CHARS = 14
ABN_DIGITS = 11

VALID_ABN = '73 790 446 591'

WEIGHTING = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
MODULUS = 89

def format(abn):
    """Format an ABN using standard spacing.

    Args:
        abn: An 11 digit ABN string.

    Returns:
        ABN in the standard format 'XX XXX XXX XXX'.

    """
    return "{}{} {}{}{} {}{}{} {}{}{}".format(*abn)



def validate(abn):
    """Validate an ABN.

    This doesn't verify that the ABN actually exists, only that looks right and
    the checksum matches.

    Args:
        abn: The ABN to validate as integer or string. May contain whitespace.

    Returns:
        Formatted ABN as a string if valid, otherwise False.

    """
    abn = str(abn)

    if len(abn) > ABN_MAX_CHARS:
        return False

    abn = [int(c) for c in abn if c.isdigit()]

    if len(abn) != ABN_DIGITS:
        return False

    # To verify the ABN according to publication "NAT 2956-7.2000", we subtract
    # 1 from the leading digit and take the dot product modulo 89. This will
    # equal zero for a valid ABN.
    temp_abn = copy.copy(abn)
    temp_abn[0] -= 1
    remainder = sum(map(operator.mul, temp_abn, WEIGHTING)) % MODULUS
    if remainder != 0:
        return False

    return format(abn)
