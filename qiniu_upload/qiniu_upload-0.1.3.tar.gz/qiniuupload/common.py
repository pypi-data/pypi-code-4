#-*- coding: utf-8 -*-
import platform
from termcolor import colored

def print_color(message, color):
    if platform.system().lower() == 'windows':
        print(message)
    else:
        print(colored(message, color))
