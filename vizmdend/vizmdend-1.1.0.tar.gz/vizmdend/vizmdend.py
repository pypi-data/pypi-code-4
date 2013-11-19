#!/usr/bin/python
'''
Created on Nov 1, 2013

@author: jbq
'''
import reader

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description='Plot a field from mdend AMBER file')
    p.add_argument('mdendfile', help='mdend file name')
    p.add_argument('yfield', help='name of the field to plot')
    p.add_argument('--xfield', help='optional field to be used as x-axis')
    args=p.parse_args()
    

    vizm = reader.Reader()
    vizm.parse(args.mdendfile)
    vizm.plot(args.yfield, args.xfield)