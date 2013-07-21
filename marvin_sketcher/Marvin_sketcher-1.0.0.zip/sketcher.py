"""
    This is module "sketcher.py" and it read the text file called sketch.txt.
    Then this program print each line in the text file
    with ' said : ' between the role's name and his lines .

    PS: This program will omit all the lines without ':' 
"""

from __future__ import print_function
import os

print('The current work path:')
print(os.getcwd())
print('\t')

try:
    data = open('sketch.txt')

    for each_line in data:
        try:
                (role, line_spoken) = each_line.split(':', 1)
                print(role, end=' ')
                print('said:', end='')
                print(line_spoken, end='')
        except ValueError:
            pass

    data.close()
except IOError:
    print('The data file is missing!')
