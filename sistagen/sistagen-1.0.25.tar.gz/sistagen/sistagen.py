# -*- coding: utf-8 -*-

import logging
from arguments import parse_arguments





def main():
    logging.basicConfig(format='%(message)s', level=logging.WARN)
        
    OPTIONS, FILES = parse_arguments()

    if not FILES:
        logging.warn('Reading configuration from stdin (Ctrl+D to finish)')
        
        import sys
        cnt = sys.stdin.read()
        
        from cfgparser import parse
        import pyparsing
        try:
            decls = parse(cnt, OPTIONS)
        except pyparsing.ParseException as pe:
            from cfgparser import print_parse_error
            print_parse_error(pe, cnt)
    else:
        from cfgparser import load_config
        decls = load_config(FILES, OPTIONS)
    
    if OPTIONS['print-templates']:
        logging.info('Available templates:')
    
    for name, decl in decls.items():
        if not decl.is_graph():
            if OPTIONS['print-templates']:
                logging.warn('\t%s' % name)
            continue

        if not OPTIONS['preserve']:
            logging.info('Graphing %s' % name)
            
        if 'out-dir' in OPTIONS:
            decl.output_dir(OPTIONS['out-dir'])

        for g in decl.get_graph():
            if OPTIONS['cmd-line']:
                logging.info('Command line to generate graph "%s" (size: %sx%s)' % (name, g.get_width, g.get_height))
                logging.warn('rrdtool graph \\')
                logging.warn(' \\\n'.join(['\t"'+arg+'"' for arg in g.prepare_args()]))
                
            if not OPTIONS['preserve']:
                logging.info('\t- %sx%s: %s' % (g.get_width, g.get_height, g.get_filename))
                g.graph()


if __name__ == '__main__':
    main()
