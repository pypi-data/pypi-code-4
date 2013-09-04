#!/usr/bin/env python
#-*- coding: utf-8 -*-


class A(object):
    def __new__(cls, temp):
        print(1, temp)
        return super(A, cls).__new__(cls)

    def __init__(self, temp):
        print(2, temp)


def main():
    a = A(3)

if __name__ == "__main__":
    main()
