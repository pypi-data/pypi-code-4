# -*- coding: utf-8 -*-
"""
Command line action to build a project

NOTE: Alpha code
"""
import datetime, os

from argh import arg

from babel.messages.pofile import read_po

from optimus.logs import init_logging

@arg('--settings', default='settings', help="Python path to the settings module")
@arg('--source', default=None, help="PO File path")
@arg('--loglevel', default='info', choices=['debug','info','warning','error','critical'], help="The minimal verbosity level to limit logs output")
@arg('--logfile', default=None, help="A filepath that if setted, will be used to save logs output")
def po(args):
    """
    Build elements for a project
    """
    starttime = datetime.datetime.now()
    # Init, load and builds
    root_logger = init_logging(args.loglevel.upper(), logfile=args.logfile)
    
    # Only load optimus stuff after the settings module name has been retrieved
    os.environ['OPTIMUS_SETTINGS_MODULE'] = args.settings
    from optimus.conf import settings, import_project_module
    from optimus.builder.assets import register_assets
    from optimus.builder.pages import PageBuilder
    from optimus.utils import initialize, display_settings
    
    display_settings(settings, ('DEBUG', 'PROJECT_DIR','SOURCES_DIR','TEMPLATES_DIR','PUBLISH_DIR','STATIC_DIR','STATIC_URL'))
    
    if hasattr(settings, 'PAGES_MAP'):
        root_logger.info('Loading external pages map')
        pages_map = import_project_module(settings.PAGES_MAP)
        setattr(settings, 'PAGES', pages_map.PAGES)
        
    print "SOURCE:", args.source
    print
    
    if os.path.exists(args.source):
        po_source = open(args.source, "r")
        catalog = read_po(po_source, ignore_obsolete=True)
        
        msgs = []
        for message in catalog:
            if message.id:
                print (message.id, message.string)
                #print ' ', (message.locations, message.flags)
                #print ' ', (message.user_comments, message.auto_comments)
                msgs.append((message.id, ''.join(message.string)))
    
    from openpyxl import Workbook
    wb = Workbook()
    
    ws = wb.create_sheet(title="foo")
    for item in msgs:
        ws.append(item)
        
    wb.save(filename="foo.xlsx")

    endtime = datetime.datetime.now()
    root_logger.info('Done in %s', str(endtime-starttime))
