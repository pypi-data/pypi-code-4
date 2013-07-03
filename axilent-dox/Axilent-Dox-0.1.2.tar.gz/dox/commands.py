"""
Command line tool.
"""
import sys
from dox.config import init_environment, get_keyfields, get_cfg, write_keyfields, get_keymap, write_keymap, clean_hashes, is_modified, write_hash
from dox.client import ping_library, get_content_keys, get_content_item
from os import walk, getcwd
from dox.uploader import upload_document, find_key, extract_keyfield
import os.path

def init(args):
    """
    Initialize the Dox environment.
    """
    if not (args.library_key and args.project and args.content_type and args.body_field):
        print 'You must specify the library key, project, content type and body field to initialize the environment.'
        sys.exit(1)
    
    print 'Dox -----------------------------------------'
    print 'Initializing environment with:'
    print 'Library Key',args.library_key
    print 'Project',args.project
    print 'Content Type',args.content_type
    print 'Body Field',args.body_field
    print 'Key Field',args.key_field
    print '---------------------------------------------'
    
    init_environment(args)
    
    print 'Environment initialized.'
    
    print 'Testing environment...'
    ping_library()
    print 'Connection settings are good.'

def up(args):
    """
    Alias for upload.
    """
    return upload(args)

def upload(args):
    """
    Uploads documents.
    """
    print 'Uploading documents...'
    keymap = get_keymap()
    keyfields = get_keyfields()
    for root, dirs, files in walk(getcwd()):
        if 'env' in dirs:
            dirs.remove('env') # don't walk into environment
        
        for name in files:
            if name.endswith('.md'):
                path = os.path.join(root,name)
                if is_modified(path):
                    print 'Uploading',name
                    key = find_key(path,keymap,keyfields)
                    key, created = upload_document(path,key=key)
                    write_hash(path)
                    if created:
                        print 'Created new content item',key
                        keymap[path] = key
                        keyfield = extract_keyfield(path)
                        print 'assigning key',key,'to keyfields',keyfields,'under keyfield',keyfield
                        keyfields[keyfield] = key
                else:
                    print name, 'not modified. Skipping.'
    
    write_keyfields(keyfields)
    write_keymap(keymap)


def keyfields(args):
    """
    Synchronizes the local cache of keyfield / key data.
    """
    print 'Synchronizing keyfield cache.'
    cfg = get_cfg()
    keyfield_name = cfg.get('Connection','key_field')
    keyfield_data = {}
    keys = get_content_keys()
    for key in keys:
        content_item = get_content_item(key)
        keyfield_data[content_item['data'][keyfield_name]] = key
        print 'Mapping',content_item['data'][keyfield_name],'to',key
    write_keyfields(keyfield_data)
    print 'Keyfield cache synchronized.'

def clean(args):
    """
    Cleans out the local hash directory - essentially marking all
    the local markdown files as modified.
    """
    print 'Cleaning out local file records.  All local files eligible for upload.'
    clean_hashes()
