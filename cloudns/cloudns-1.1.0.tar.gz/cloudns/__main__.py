#!/usr/bin/env python
# coding=utf-8

"""cloudns as a cli tool

"""

import cloudns
import json


def main():
    u = cloudns.User(passport='dw_songyuanle',
                     token='566EFCC953985ACD0EAAA8A5D6187D9C')
    # r = u.get_all_zones()
    # r = u.get_all_records('yygamedev.com', offset=180, limit=10)
    r = u.search_record('yygamedev.com', '*t*t*')
    print json.dumps(r, indent=4)


if __name__ == '__main__':
    main()
