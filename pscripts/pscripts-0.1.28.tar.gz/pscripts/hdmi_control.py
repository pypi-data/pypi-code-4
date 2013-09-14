#!/usr/bin/env python

from subprocess import check_output, call
from re import search 

line_pattern = r"(.*) \d\.\d"
adjust_brightness_step_val = 0.1

##########################
# API

def increase_brightness():
    line = get_brightness_line()
    val = extract_brightness(line)
    new_val = increment(val)
    set_brightness(new_val)

def decrease_brightness():
    line = get_brightness_line()
    val = extract_brightness(line)
    new_val = decrement(val)
    set_brightness(new_val)


##########################
# HELPERS

def increment(start):
    if start <= 1.0 - adjust_brightness_step_val:
        return 1.0
    return round(start + adjust_brightness_step_val, 1)

def decrement(start):
    if start >= 0 + adjust_brightness_step_val:
        return 0.0
    return round(start - adjust_brightness_step_val, 1)

def set_brightness(val):
    # xrandr --output HDMI1  --brightness .5
    cmd = "xrandr --output HDMI1  --brightness " + str(val)
    call(cmd.split())

def get_brightness_line():
    cmd = "xrandr --current --verbose | grep -A5 'HDMI1' | tail -1"
    output = check_output(cmd, shell=True)
    return output

def extract_brightness(line):
    # sample: b'\tBrightness: 0.50\n'
    pattern = r".* (\d\.\d)"
    match = search(pattern, line)
    val = round(float(match.group(1)), 1)    

##########################
# TESTS

def _test():
    test_line_rewrite()
    test_numbers_only()

# UNIT-TESTS
def test_extract_brightness():
    sample_line = b'\tBrightness: 0.50\n'
    expected = 0.5
    result = extract_brightness(sample_line)
    assert expect == result

def test_numbers_only():
    b = 1.0
    a = 0.9
    res = decrement(b, adjust_brightness_step_val)
    assert a == res

if __name__ == '__main__':
    _test()
