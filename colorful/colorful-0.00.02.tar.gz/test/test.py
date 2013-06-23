#!/usr/bin/python

from colorful import Colorful

if __name__ == "__main__":
    print(Colorful.bold_red_on_black("Hello World"))
    print(Colorful.black_on_white("Hello World!"))
    print(Colorful.underline("Hello World"))
    print(Colorful.bold_and_underline_green("Hello World!"))
    print(Colorful.bold_and_underline_green_on_red("Hello World!"))
    print(Colorful.bold_and_underline_and_strikethrough_green_on_red("Hello World!"))
    print(Colorful.strikethrough("dfgsfdg"))
    Colorful.out.bold_red_on_black("dfgdfg")
