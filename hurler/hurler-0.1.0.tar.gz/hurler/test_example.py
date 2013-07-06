from __future__ import absolute_import
from __future__ import unicode_literals
"""
Note: This file shows a very verbose method of using hurler. Actual code
would often be less code than this example.

The example illustrates how to use the callback system, together with the
hurler filters. It does this by implementing a small dice rolling program.

It does this by registering several functions for printing out the dice
result. Each function then uses a filter to ensure it only gets called
if the result matches with what they are made for. (i.e. a print callback
that tells you the result was 1, only gets called if the result is actually 1)
"""
import random

from .callbacks import Callbacks
from .filters import filter


callback_register = Callbacks()


@filter
def dice_result(equal=None, higher_than=None, lower_than=None):
    """
    A simple filter that checks if the given result is higher, lower than or
    equal to the passed value. It only supports one at a time though.
    """
    if not equal is None:
        return (lambda result: result == equal)
    if not higher_than is None:
        return (lambda result: result > higher_than)
    if not lower_than is None:
        return (lambda result: result < lower_than)
    raise ValueError("Missing argument, need at least one.")


def test_main():
    # Send an event to roll 1 dice
    callback_register.call("dice_roll")
    # Send an event to roll several dices
    callback_register.call("dice_roll", 6)
    # Send an event to roll a dice with many faces.
    callback_register.call("dice_roll", 50)


@callback_register.register("dice_roll")
def roll_dice(amount_of_dice=1, faces=6):
    """
    A simple callback that rolls a dice and calls all callbacks
    registered for the event `dice_result` with each result found.

    :param amount_of_dice: The amount of dices to roll.
    :param faces: The amount of faces each dice has.
    """
    for n in range(amount_of_dice):
        # Use random to get our dice result
        result = random.choice(range(1, faces + 1))
        # Now we call the dice_result event
        callback_register.call("dice_result", result)


# The following functions will print our result when a dice rolls
# Note: These are overly verbose.
@callback_register.register("dice_result")
@dice_result(higher_than=3)
def print_high_result(result):
    """
    Function that prints all higher than 3 rolls.
    """
    print("You rolled higher than 3! To be exact you rolled %d" % result)
    assert result > 3


@callback_register.register("dice_result")
@dice_result(equal=3)
def print_three_message(result):
    """
    Function that prints all results equal to 3.
    """
    print("You rolled midway 3! (%d)" % result)
    assert result == 3


@callback_register.register("dice_result")
@dice_result(equal=2)
def print_two_message(result):
    """
    Function that prints all results equal to 2.
    """
    print("You rolled a little 2! (%d)" % result)
    assert result == 2


@callback_register.register("dice_result")
@dice_result(equal=1)
def print_one_message(result):
    """
    Function that prints all results equal to 1.
    """
    print("You only rolled a 1! (%d)" % result)
    assert result == 1
