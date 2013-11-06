#!/usr/bin/env python
"""Generic utility functions for sitemap.xml maintenance and publishing."""

from sitemap_gen import CreateSitemapFromFile

__all__ = ['update_or_create_sitemap']

def update_or_create_sitemap(outfile='sitemap.xml', notify=False):
    """Simple wrapper for easy sitemap.xml creation using the
    ``CreateSitemapFromFile`` function"""
    # SITEMAP_SUPPRESS_NOTIFY = disables pinging google if set to False
    # SITEMAP_PATH = /path/to/sitemap.xml
    try:
        sitemap = CreateSitemapFromFile(
            outfile,
            suppress_notify=notify)
    except:
        raise 
    # generate or update(?) the actual sitemap.xml file
    sitemap.Generate()
    return None
    

