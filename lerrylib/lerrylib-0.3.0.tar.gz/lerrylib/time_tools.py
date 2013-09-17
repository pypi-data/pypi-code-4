#!/usr/bin/env python
#coding:utf-8
import time

def today_start():
    li = list(time.localtime())[:3]+[0]+[0]*5
    return int(time.mktime(li))

if __name__ == "__main__":
    print today_start()
