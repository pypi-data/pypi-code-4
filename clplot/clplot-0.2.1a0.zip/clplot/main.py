#!/usr/bin/env python


import os
import argparse
import re

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec


#-----------------------------------------------------------------------------
# exception handling
#-----------------------------------------------------------------------------
class PlotError(Exception):
    pass

#-----------------------------------------------------------------------------
# helper functions
#-----------------------------------------------------------------------------
def _calc_grid(plots_per_fig):
    """Compute the number of rows and columns to give a squarish grid"""
    nr = np.floor(np.sqrt(plots_per_fig))
    nc = np.ceil(plots_per_fig/nr)
    gridshape = (np.int(nr), np.int(nc))
    return gridshape

def _parse_data(fpath, datastep, delimiter=','):
    """Read the input csv file into a record array"""
    idata = np.recfromcsv(fpath, case_sensitive=True, delimiter=delimiter)
    data = idata[::datastep]
    data_fields = data.dtype.names
    return (data, data_fields)

def _add_pattern_matches_to_list(regex, lst, master):
    """Add items matching a regular expression to a list"""
    pat = re.compile(regex)
    found = False
    for df in master:
        if pat.match(df):
            found = True
            m = pat.match(df).group()
            if m not in lst:
                lst.append(m)
    if not found:
        raise PlotError('Unable to find column names corresponding to specified regular expression \'%s\'.' % regex)
    return lst

def printtable(rows):
    """From http://stackoverflow.com/questions/5909873/python-pretty-printing-ascii-tables"""
    if len(rows) > 1:
        headers = rows[0]._fields
        lens = []
        for i in range(len(rows[0])):
            lens.append(len(max([x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
            if isinstance(rows[0][i], int):
                formats.append("%%%dd" % lens[i])
            else:
                formats.append("%%-%ds" % lens[i])
            hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        print hpattern % tuple(headers)
        print separator
        for line in rows:
            print pattern % tuple(line)
    elif len(rows) == 1:
        row = rows[0]
        hwidth = len(max(row._fields,key=lambda x: len(x)))
        for i in range(len(row)):
            print "%*s = %s" % (hwidth,row._fields[i],row[i])


#-----------------------------------------------------------------------------
# the main plotting function
#-----------------------------------------------------------------------------
def plot(fpath, datastep=1, delimiter=',', colnames=[], colnames_regex=None, xcolname=None, 
         excludes=[], excludecolnames_regex=None,
         plots_per_fig=9, figsize=(14.0, 8.0), maxfigs=10, pad=1.0, wpad=2.0, hpad=2.0, 
         linecolor='black', linewidth=2, linestyle='-', fontsize=14.0, 
         listcols=False, info=False):

    # parse the data to a format that is easily accessed by column name
    (data, data_fields) = _parse_data(fpath, datastep, delimiter=delimiter)

    # if the user wants a column listing, print the values and exit
    if listcols:
        print data_fields
        return None

    # if the user didn't specify column names, add all of the fields found in the file
    if not (colnames or colnames_regex):
        colnames = data_fields

    # add column names based on a regular expression
    if colnames_regex:
        colnames = _add_pattern_matches_to_list(colnames_regex, colnames, data_fields)
    
    # if no value was given for xcolname, default to the name of the first field 
    if not xcolname:
        xcolname = data_fields[0]
    xdata = data[xcolname]

    # add xcolname to the exclude list (column names to be excluded when plotting)
    excludes.append(xcolname)

    # add columns to the exclude list based on a regular expression
    if excludecolnames_regex:
        excludes = _add_pattern_matches_to_list(excludecolnames_regex, excludes, colnames)

    # actually exclude the specified columns names from the list of columns to plot
    colnames = [cn for cn in colnames if cn not in excludes]

    # if we ended up with no columns, raise an error
    if not colnames:
        raise PlotError('Nothing to plot. Perhaps the delimiter is incorrect or all columns that were specified were excluded.')

    # if requested, print a statistics table for the chosen columns
    if info:
        from collections import namedtuple
        trow = namedtuple('trow', ['col','name','min','max','mean','std'])
        ncols = len(colnames)
        nrows = data[xcolname].shape
        print 'Number of dependent variable columns specified: %i' % ncols
        print 'Number of rows: %i' % nrows
        all_data = []
        for i, cn in enumerate(colnames):
            d = data[cn]
            all_data.append(trow(str(i), cn, '%.3g' % d.min(), '%.3g' % d.max(), '%.3g' % d.mean(), '%.3g' % d.std(),))
        printtable(all_data)
        return

    # check to see if we are trying to create more figures than the specified maximum number
    nfigs = np.ceil(len(colnames)/float(plots_per_fig))
    if nfigs > maxfigs:
        raise PlotError('The number of figures to be created is large (%i). If you wish to create this many figures, increase the value using the \'maxfigs\' argument in the function call or the \'--maxfigs\' command line option.' % nfigs)

    # create a data structure that makes it convenient to create a number of subplots on a given figure:
    #  - divide colnames up into groups of length plots_per_fig
    #  - each group will go on a different figure
    fig_items = [colnames[i:i+plots_per_fig] for i in range(0, len(colnames), plots_per_fig)]
    gridshape = _calc_grid(plots_per_fig)

    # create each figure
    for f in fig_items:
        fig = plt.figure(figsize=figsize)
        # create each subplot on the figure
        for i, cname in enumerate(f):
            ydata = data[cname]
            subplot_loc = np.unravel_index(i, gridshape)  # find the (i,j) location from a linear index
            axes = plt.subplot2grid(gridshape, subplot_loc)
            axes.set_xlabel(xcolname, fontsize=fontsize)
            axes.set_ylabel(cname, fontsize=fontsize)
            axes.plot(xdata, ydata, color=linecolor, linewidth=linewidth, linestyle=linestyle)
        fig.tight_layout(pad=pad, w_pad=wpad, h_pad=hpad)
    plt.show()


def main():
    """main entry point with command line parsing"""
    
    parser = argparse.ArgumentParser()

    parser.add_argument('filename', help='Name (including the path) of the csv file to be plotted', 
                        metavar='FILENAME', type=argparse.FileType('r'))

    parser.add_argument('-l', '--listcols', action='store_true',
                        help='List all of the data column names and exit')

    parser.add_argument('-i', '--info', action='store_true',
                        help='List information about the selected data columns and exit')

    parser.add_argument('-c', '--colname', action='append', dest='colnames', metavar='COLNAME',
                        default=[], help='Name of columns to include in plotting. By default, all columns are plotted.')

    parser.add_argument('-cr', '--colname_regex', action='store', dest='colnames_regex', metavar='COLNAMEREGEX',
                        help='A regular expression for the names of columns to include in plotting. By default, all columns are plotted.')

    parser.add_argument('-e', '--excludecolname', action='append', dest='excludes', metavar='EXCLUDECOLNAME',
                        default=[], help='Name of a column to exclude from plotting.')

    parser.add_argument('-er', '--excludecolname_regex', action='store', dest='excludecolnames_regex', metavar='EXCLUDECOLNAMEREGEX',
                        help='A regular expression for the names of columns to exclude from plotting')

    parser.add_argument('-d', '--delimiter', action='store', dest='delimiter', metavar='DELIMITER',
                        default=',', help='The data delimited (e.g., ",", "\t")', type=str)

    parser.add_argument('-x', '--xcolname', action='store', dest='xcolname', metavar='XCOLNAME',
                        help='Name of the column containing the independent variable value. By default, the first column is used.')

    parser.add_argument('-s', '--step', action='store', dest='datastep', metavar='STEP',
                        default=1, help='Data skip step (::step)', type=int)

    parser.add_argument('-n', '--num_plots_per_fig', action='store', dest='plots_per_fig', metavar='NUMPLOTSPERFIG',
                        default=9, help='Number of plots per figure', type=int)

    parser.add_argument('--maxfigs', action='store', dest='maxfigs', metavar='MAXFIGS',
                        default=10, help='Maximum number of figures that can be created', type=int)

    parser.add_argument('--linecolor', action='store', dest='linecolor', metavar='LINECOLOR',
                        default='black', help='The color for the plot lines', type=str)

    parser.add_argument('--linewidth', action='store', dest='linewidth', metavar='LINEWIDTH',
                        default=2, help='The width for the plot lines', type=float)

    parser.add_argument('--linestyle', action='store', dest='linestyle', metavar='LINESTYLE',
                        default='-', help='The style for the plot lines', type=str)

    parser.add_argument('--fontsize', action='store', dest='fontsize', metavar='FONTSIZE',
                        default=14.0, help='The font size for the axis labels', type=float)

    args = parser.parse_args()

    plot(args.filename, datastep=args.datastep, delimiter=args.delimiter,
         plots_per_fig=args.plots_per_fig, colnames=args.colnames, 
         colnames_regex=args.colnames_regex, 
         excludecolnames_regex=args.excludecolnames_regex,
         xcolname=args.xcolname, excludes=args.excludes,
         maxfigs=args.maxfigs, listcols=args.listcols, info=args.info,
         linecolor=args.linecolor, linewidth=args.linewidth, 
         linestyle=args.linestyle, fontsize=args.fontsize)

#-----------------------------------------------------------------------------

if __name__ == '__main__':
    main()
