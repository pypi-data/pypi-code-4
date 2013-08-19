#! /usr/bin/env python
#
#        \file miscTools.py
#  
#        \author Fraser Newton
# 
#        Date Created: 2006-02-02T10:21:12-0700\n
#        Date Modified:
# 
#        Copyright 2004-2005 Random Knowledge Inc.\n
#        All Rights Reserved
#

def parseArgs(short_options, long_options={}, man = ''):
    import sys, getopt, re

    if not long_options.has_key('help'): long_options['help'] = 'display help'
    short_options_str = ''.join(map(lambda x: str(x[0]), short_options.items()))
    (opts,args_proper) = getopt.getopt(sys.argv[1:],short_options_str, map(lambda x: x[0], long_options.items()))

    opts_dict = dict(opts)

    if opts_dict.has_key('--help'):        
        print 'man: %s\n\noptions:\n%s\n%s\n' % (man,
                                                 '\n'.join(map(lambda x: '-'+x[0].strip(' ')+'\t'+str(x[1]),
                                                    short_options.items())),
                                                 '\n'.join(map(lambda x: '--'+x[0].strip(' ')+'\t'+str(x[1]),
                                                               long_options.items())))
        sys.exit(0)

    for itm_short in filter(lambda x: re.compile(r'.*:').match(x),map(lambda x: x[0],short_options.items())):
        itm_key = '-'+itm_short.strip(' :')
        if not opts_dict.has_key(itm_key):
            if type(short_options[itm_short]) == type(()):
                sys.stderr.write('using default for %s\n' % itm_short)
                opts_dict['-'+itm_short.strip(': ')] = short_options[itm_short][1]
            else:
                sys.stderr.write('%s is a required option\n' % itm_short)
                sys.exit(1)

    for itm_long in filter(lambda x: re.compile(r'.*=').match(x),map(lambda x: x[0],long_options.items())):
        itm_key = '--'+itm_long.strip(' =')
        if not opts_dict.has_key(itm_key):
            if type(long_options[itm_long]) == type(()):
                sys.stderr.write('using default for %s\n' % itm_long)
                opts_dict['--'+itm_long.strip('= ')] = long_options[itm_long][1]
            else:
                sys.stderr.write('%s is a required option\n' % itm_long)
                sys.exit(1)


        
    return opts_dict

    
        
