
#! /usr/bin/python
# -*- coding: utf-8 -*-


#If you have any questions, please contact any of the following:
#Evan(evan176@hotmail.com)

import numpy

def loadcsv(fname):#Load csv file to numpy 2-array,but file must keep first feature row

    try:
        csv_file = open(fname, 'rb')
        data = numpy.loadtxt(csv_file, delimiter=',', skiprows=1)
        return data
    except:
        print "\n===Error in load-loadcsv : path or file is wrong==="
        return False

def loadnpy(fname):#Load csv file to numpy 2-array,but file must keep first feature row

    try:
        data = numpy.load(fname)
        return data
    except:
        print "\n===Error in load-loadnpy : path or file is wrong==="
        return False

#====================================Test Area====================================
