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

from PySide import QtCore
from PySide import QtGui
from PySide import QtDeclarative
from threading import Thread, Event
from queue import Queue, Empty
from pprint import pprint
from os import path
import logging

import jsonrpclib

from squeezeui.controllers.config import max_items, config
from squeezeui.controllers import protocol, tools
from squeezeui.models.listmodel import MenuItem, MediaListModel

# signal the background-thread to finish
end = Event()
# commands from qml ui
cmdqueue = Queue()
menuqueue = Queue()


class Player(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self._status = tools.NDict()
        self._menu = MediaListModel([])
        self._popup = ''
        self._thread = Thread(target=self.run_thread)
        self._thread.start()
                
    def run_thread(self):
        self.remote =  jsonrpclib.Server(protocol.get_jsonrpc_url())
        self._set_home_menu()
        while not end.is_set():
            try:
                self._set_player_param(cmdqueue.get(timeout=0.3))
            except Empty:
                pass
            try:
                self._set_player_menu(menuqueue.get(timeout=0.3))
            except Empty:
                pass
            
            self._get_player_status()

    def _set_home_menu(self):
        if len(self._menu) > 0:
            self._menu.clear()
            
        self._menu.extend([
            MenuItem(item, no) for no, item in enumerate(
                protocol.build_home_menu())])

    def _set_settings_menu(self):
        if len(self._menu) > 0:
            self._menu.clear()
            
        self._menu.extend([
            MenuItem(item, no) for no, item in enumerate(
                protocol.build_settings_menu())])

    def _set_playlist_menu(self):
        if len(self._menu) > 0:
            self._menu.clear()
            
        self._menu.extend([
            MenuItem(item, no) for no, item in enumerate(
                protocol.build_playlists_menu())])

    def _set_player_param(self, param):
        try:
            self.remote.slim.request(config['mac'], param)
        except Exception as e:
            logging.exception("remote.slim.request")
            self._set_popup(repr(e))
            
    def _set_player_menu(self, param):
        if protocol.handle_internal_cmd(param):
            self._set_popup('{0}'.format(param.get('name', '')))
            return
        else:
            if '_user_action' in param and param['_user_action'] == 'add':
                self._set_popup('Added {0}'.format(param['name']))
                
            try:
                request, source = protocol.build_slim_request(param)
                # pprint(request)
            except Exception as e:
                logging.exception('build_slim_request')
                self._set_popup(repr(('build_slim_request', e)))
                return
        
        try:
            res = self.remote.slim.request(*request)
            # pprint(res)
            
            param['name'] = '..' # use this to go back!
            if (len(res) > 0):
                loop = None
                count = 0
                for k, v in res.items():
                    if 'loop' in k:
                        loop = v
                        for i in loop:
                            i.update(_source=source, _back=param)
                    elif 'count' in k:
                        count = v
                
                if loop:
                    self._menu.clear()
                    
                    if not '_back' in param:
                        param['_back'] = dict(
                            name='..',
                            type='back_to_{}'.format(param['type']))
                            
                    self._menu.append(MenuItem(param['_back'], -1))
                        
                    self._menu.extend(
                        [MenuItem(item, no) for no, item in enumerate(loop)])
                    
                    if int(count) > max_items:
                        more_param = param.copy()
                        more_param['_start'] = param.get('_start', 0) + max_items
                        more_param['name'] = 'More ...'
                        self._menu.append(MenuItem(more_param, -1))
                        
        except KeyError as e:
            # pprint((e, param, res))
            logging.exception('remote.slim.request')
            self._set_popup(repr(('slim.request', e)))
            
        except Exception as e:
            # pprint((e, [config['mac'], param]))
            logging.exception('remote.slim.request')
            self._set_popup(repr(('slim.request', e)))
            
    def _get_player_status(self):
        try:
            status = self.remote.slim.request(
                config['mac'], ['status', '-', 1, 'tags:cgABbehldiqtyrSuoKLNJ'])
                # 'tags:uB'])
            changed = False
            def _status_updated(name, old, new):
                nonlocal changed
                if name == 'status.time':
                    self.on_newdata.emit()
                elif name == 'status.player_name':
                    self.on_new_player.emit(new)
                else:
                    if not changed:
                        changed = True
                
            self._status.update(status, _status_updated)
            
            if (changed):
                self.on_new_song_info.emit()
            
        except Exception as e:
            # logging.exception('_get_player_status', e)
            self._status.clear()
            self._set_popup('jsonrpc ERROR')
            
    def _get_name(self):
        return self._status.get('player_name', '')

    def _get_song(self):
        return self._status.get('playlist_loop', [{}])[0].get('title', '')

    def _get_artist(self):
        return self._status.get('playlist_loop', [{}])[0].get('artist', '')
        
    def _get_album(self):
        return self._status.get('playlist_loop', [{}])[0].get('album', '')
        
    def _get_meta(self):
        song = self._status.get('playlist_loop', [{}])[0]
        if 'remote_title' in song:
            return song['remote_title']
        else:
            return ''
            
    def _get_cover(self):
        song = self._status.get('playlist_loop', [{}])[0]
        if 'artwork_url' in song:
            return protocol.build_img_url(song['artwork_url'])
        else:
            return protocol.build_img_url('music/{}/cover.jpg'.format(
                song.get('coverid', '0')))
        
    def _get_volume(self):
        return int(self._status.get('mixer volume', 100))

    def _get_time(self):
        return float(self._status.get('time', 0.0))
        
    def _get_duration(self):
        return float(self._status.get('duration', 0.0))
        
    def _get_timeplayed(self):
        t = self._get_time()
        return '{:0.0f}:{:02.0f}'.format(t // 60, t % 60)
        
    def _get_timeleft(self):
        t = self._get_time() - self._get_duration() 
        return '{:0.0f}:{:02.0f}'.format(t // 60, t % 60)
            
    def _get_menu(self):
        return self._menu

    def _get_popup(self):
        return self._popup

    def _set_popup(self, text):
            self._popup = text
            self.on_popup.emit()
            
    on_newdata = QtCore.Signal()
    on_new_player = QtCore.Signal(str)
    on_new_song_info = QtCore.Signal()
    on_popup = QtCore.Signal()
    
    name = QtCore.Property(str, _get_name, notify = on_new_song_info)
    song = QtCore.Property(str, _get_song, notify = on_new_song_info)
    artist = QtCore.Property(str, _get_artist, notify = on_new_song_info)
    album = QtCore.Property(str, _get_album, notify = on_new_song_info)
    meta = QtCore.Property(str, _get_meta, notify = on_new_song_info)
    cover = QtCore.Property(str, _get_cover, notify = on_new_song_info)
    time = QtCore.Property(float, _get_time, notify = on_newdata)
    volume = QtCore.Property(int, _get_volume, notify = on_new_song_info)
    timeplayed = QtCore.Property(str, _get_timeplayed, notify = on_newdata)
    timeleft = QtCore.Property(str, _get_timeleft, notify = on_newdata)
    duration = QtCore.Property(float, _get_duration, notify = on_newdata)
    menuModel = QtCore.Property(QtCore.QObject, _get_menu, constant=True)
    popup = QtCore.Property(str, _get_popup, notify = on_popup)
    
    @QtCore.Slot()
    def button_jump_rew(self):
         cmdqueue.put(['button', 'jump_rew'])
         
    @QtCore.Slot()
    def button_jump_fwd(self):
         cmdqueue.put(['button', 'jump_fwd'])
         
    @QtCore.Slot()
    def button_pause(self):
         cmdqueue.put(['pause'])
         
    @QtCore.Slot()
    def button_play(self):
         cmdqueue.put(['play'])

    @QtCore.Slot(float)
    def slider_time(self, value):
         cmdqueue.put(['time', value])
         
    @QtCore.Slot(int)
    def slider_volume(self, value):
         cmdqueue.put(['mixer', 'volume', value])

    @QtCore.Slot()
    def media_home(self):
        self._set_home_menu()
        
    @QtCore.Slot()
    def media_settings(self):
        self._set_settings_menu()
        
    @QtCore.Slot()
    def media_playlist(self):
      self._set_playlist_menu()

    @QtCore.Slot(QtCore.QObject, str)
    def media_search(self, wrapper, search):
        wrapper._media._items['_user_action'] = 'search'
        wrapper._media._items['_search'] = search
        menuqueue.put(wrapper._media._items)
    
    @QtCore.Slot(QtCore.QObject)
    def media_selected(self, wrapper):
        # print ('User selected:', wrapper._media.name.encode('utf8'))
        if wrapper._media.type == 'back_to_mainmenu':
            self._set_home_menu()
            
        elif wrapper._media.type == 'back_to_settingsmenu':
            self._set_settings_menu()
            
        elif wrapper._media.type == 'back_to_playlistmenu':
            self._set_playlist_menu()
            
        elif ('search' in wrapper._media.type) and (
            not '_search' in wrapper._media._items):
                logging.debug('User want to search: %s %s',
                    wrapper._media.name.encode('utf8'),
                    wrapper._media.type)
                    
        elif 'text' in wrapper._media.type:
            pass
        
        else:
            wrapper._media._items['_user_action'] = 'select'
            menuqueue.put(wrapper._media._items)

    @QtCore.Slot(QtCore.QObject)
    def media_play(self, wrapper):
        # print ('User played:', wrapper._media.name.encode('utf8'))
        wrapper._media._items['_user_action'] = 'play'
        menuqueue.put(wrapper._media._items)

    @QtCore.Slot(QtCore.QObject)
    def media_add(self, wrapper):
        # print ('User added:', wrapper._media.name.encode('utf8'))
        wrapper._media._items['_user_action'] = 'add'
        menuqueue.put(wrapper._media._items)


def discover_server():
    if not config['server']:
        config['server'], config['audioport'] = protocol.discover()
    if not config['mac']:
        config['mac']  = protocol.getmac()
    

def serve_forever():
    discover_server()
    player = Player()
    app = QtGui.QApplication([])
    view = QtDeclarative.QDeclarativeView()
    
    view.setWindowTitle('Squeezeui')
    view.setWindowIcon(QtGui.QIcon(path.join(
        config['datapath'], 'squeezeui', 'views', 'App.svg')))
    
    player.on_new_player.connect(view.setWindowTitle)
    
    rc = view.rootContext()
    rc.setContextProperty('player', player)
        
    view.setSource(QtCore.QUrl.fromLocalFile(
        path.join(config['datapath'], 'squeezeui', 'views', 'player.qml')))
        
    view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
    view.show()
    app.exec_()
    end.set()
