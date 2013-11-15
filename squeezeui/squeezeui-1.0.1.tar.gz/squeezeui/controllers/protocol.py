# -*- coding: utf-8 -*-
#
#  Squeezeui - Graphical user interface for Squeezebox players.
#
#  Copyright (C) 2013 Frode Holmer <fholmer+squeezeui@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from squeezeui.controllers.config import max_items, config, saveuserconfig
from webbrowser import open_new_tab
import jsonrpclib

def discover():
    from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, \
    SO_REUSEADDR, SO_BROADCAST
    
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    cs.settimeout(1.0)
    cs.sendto(b'e', ('255.255.255.255', 3483))
    ip, port = None, None
    
    data = b""
    try:
        data = cs.recvfrom(10)
        if b'E' == data[0]:
            ip, port = data[1]
    except:
        pass
    
    return ip, port

    
def getmac():
    from uuid import getnode
    mac = '{:012x}'.format(getnode())
    return ':'.join([mac[i:i+2] for i in range(0,12,2)])


def build_home_menu():
    return [
        dict(
            name='Music folder',
            type='mainmenu',
            icon='html/images/musicfolder.png',
            cmd=['musicfolder', 0, max_items]),
#        dict(
#            name='Search', 
#            type='db_search',
#            icon='html/images/search.png',
#            _source='dbsearch'),
        dict(
            name='Radio', 
            type='mainmenu',
            icon='html/images/ServiceProviders/tuneinurl.png',
            cmd=['radios', 0, max_items]),
        dict(
            name='RSS', 
            type='mainmenu', 
            icon='html/images/newmusic.png',
            cmd=['rss', 'items', 0, max_items]),
#
#   Disable my apps till i find a way to handle the redirect type.
#        dict(
#            name='My apps', 
#            type='mainmenu', 
#            icon='plugins/MyApps/html/images/icon.png',
#            cmd=['myapps', 'items', 0, max_items]),
        dict(
            name='All apps', 
            type='mainmenu', 
            icon='plugins/AppGallery/html/images/icon.png',
            cmd=['apps', 0, max_items]),
        dict(
            name='Playlists',
            type='mainmenu',
            icon='html/images/playlists.png',
            cmd=['playlists', 0, max_items]),
        dict(
            name='Favorites',
            type='mainmenu',
            icon='html/images/favorites.png',
            cmd=['favorites', 'items', 0, max_items])]


def build_settings_menu():
    return [
        dict(
            name='Select player', 
            type='settingsmenu', 
            icon='html/images/softsqueeze.png',
            cmd=['players', 0, max_items]),
        dict(
            name='Sync settings',
            type='settingsmenu',
            icon='html/images/newmusic.png',
            cmd=['syncsettings', 0, max_items]),
        dict(
            name='Sleep settings',
            type='settingsmenu',
            icon='html/images/newmusic.png',
            cmd=['sleepsettings', 0, max_items]),
        dict(
            name='System info',
            type='settingsmenu',
            icon='html/images/newmusic.png',
            cmd=['systeminfo', 'items', 0, max_items]),
        dict(
            name='Save settings to ~/.squeezeuirc', 
            type='settingsmenu', 
            icon='html/images/playlistsave.png',
            _save_config=True)]


def build_playlists_menu():
    return [
        dict(
            name='Show current playlist',
            type='playlistmenu',
            icon='html/images/playlists.png',
            cmd=["status", 0, max_items, "tags:cgABbehldiqtyrSuoKLNJ"]),
        dict(
            name='Clear current playlist',
            type='playlistmenu',
            icon='html/images/playlists.png',
            cmd=["playlist", "clear"])]


def build_img_url(thumb):
    # TODO:
    # quickfix to bypass external urls
    if '://' in thumb:
        return thumb
    # quickfix double //
    elif thumb.startswith('/'):
        return 'http://{0[server]}:{0[webport]}{1}'.format(config, thumb)
    else:
        return 'http://{0[server]}:{0[webport]}/{1}'.format(config, thumb)


class jsonrpc(object):
    connstring = 'http://{0[server]}:{0[webport]}/jsonrpc.js'
    
    def __init__(self):
        self._rpc = jsonrpclib.Server(self.connstring.format(config))
        
    def slim_request(self, *args):
        return self._rpc.slim.request(*args)

    def handle_internal_cmd(self, param):
        if 'isplayer' in param and param['isplayer'] == 1:
            config['mac'] = param['playerid']
            return True
        elif '_save_config' in param:
            saveuserconfig()
            return True
        elif '_source' in param and param['_source'] == 'rss':
            if 'link' in param:
                open_new_tab(param['link'])
                return True
        return False

    def build_slim_request(self, param):
        source = param.get('_source', '_none') # settes på grunntyper
        request = None
        start = param.get('_start', 0)

         # select in mainmenu
        if not '_source' in param:
            source = param['cmd'][0]  # settes på grunntyper
            request = (config['mac'], param['cmd'])
            
        # from current playlist                
        elif param['_source'] == 'status':
            request = (
                config['mac'],
                ['playlist', 'index', param['playlist index']])
            
        # from playlists folder
        elif param['_source'] == 'playlists':
            if 'playlist index' in param:
                request = (
                    config['mac'],
                    ['playlistcontrol','cmd:load', 'playlist_id:{}'.format(
                        param['_back']['id']), 'play_index:{}'.format(
                        param['playlist index'])])
            else:
                request = (
                    config['mac'],
                    ['playlists', 'tracks', start, max_items, 'playlist_id:{}'.format(
                        param['id'])])
    
        # from search database
        elif param['_source'] == 'dbsearch':
            if 'type' in param:
                request = (config['mac'],
                    ['search', start, max_items, 'term:{}'.format(param['_search'])])
            else:
                request = (config['mac'],
                        ['playlistcontrol', 'cmd:{}'.format('load'), 'track_id:{}'.format(
                            param['track_id'])])
        else:
            # jivemenus
            if 'actions' in param:
                _do = 'do' if 'do' in param['actions'] else 'go'
                if _do in param['actions']:
                    _cmd = param['actions'][_do]['cmd']
                    if 'params' in param['actions'][_do]:
                        _cmd += ['{}:{}'.format(*v) for v in param['actions'][_do]['params'].items()]
                    # print(_cmd)
                    request = (config['mac'], _cmd)
                else:
                    raise Exception('action missing')
            # from misc xmlbrowsers:
            elif not 'type' in param or param['type'] in (
                'audio', 'link', 'playlist', 'opml', 'lnk'):
                # play or add.
                if (param['_user_action'] in ('play', 'add')):
                    request = (config['mac'],[
                        param['_source'],
                        'playlist',
                        param['_user_action'],
                        'item_id:{}'.format(param['id'])])
        
                # play                    
                elif not 'hasitems' in param or (
                    'hasitems' in param and param['hasitems'] == 0):
                    request = (config['mac'], [
                        param['_source'], 'playlist', 'play','item_id:{}'.format(
                            param['id'])])
                    
                # select
                else:
                    request = (
                        config['mac'],
                        [param['_source'], 'items', start, max_items, 'item_id:{}'.format(
                            param['id'])])
                            
            # select from mainmenu
            elif param['type'] == 'xmlbrowser':
                source = param['cmd']
                request = (
                    config['mac'],
                    [param['cmd'], 'items', start, max_items])
    
            # selected from xmlbrowser_search
            elif param['type'] == 'xmlbrowser_search':
                request = (
                    config['mac'],
                    ['search', 'items',  start, max_items, 'search:{}'.format(
                        param['_search'])])
                        
            # selected from anywhere
            elif 'search' in param['type']:
                request = (
                    config['mac'],
                    [param['_source'], 'items', start, max_items, 'item_id:{}'.format(
                        param['id']), 'search:{}'.format(param['_search'])])
                    
            # select from musicfolder
            elif param['type'] == 'folder':
                useraction = param['_user_action']
                if useraction in ('play', 'add'):
                    _cmd = 'load' if 'play' in useraction else 'add'
                    request = (
                    config['mac'],
                    ['playlistcontrol', 'cmd:{}'.format(_cmd), 'folder_id:{}'.format(
                        param['id'])])
                else:
                    request = (
                        config['mac'],
                        ['musicfolder', start, max_items, 'folder_id:{}'.format(
                            param['id'])])
                        
            # from musicfolder
            elif param['type'] == 'track':
                _cmd = 'load' if not 'add' in param['_user_action'] else 'add'
                request = (
                    config['mac'],
                    ['playlistcontrol', 'cmd:{}'.format(_cmd), 'track_id:{}'.format(
                        param['id'])])
            
        return request, source
        