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
from squeezeui.controllers.protocol import build_img_url

# Et QT-objekt som bare inneholder et python-objekt.
# f.eks en et enkelt liste-element
class MenuWrapper(QtCore.QObject):
    def __init__(self, media):
        QtCore.QObject.__init__(self)
        self._media = media
 
    def _name(self):
        return str(self._media)
 
    def _thumb(self):
        return self._media.thumb
    
    def _issearch(self):
        return self._media.isSearch
        
    changed = QtCore.Signal()
    name = QtCore.Property(str, _name, notify=changed)
    thumb = QtCore.Property(str, _thumb, notify=changed)
    isSearch = QtCore.Property(bool, _issearch, notify=changed)

    def __repr__(self):
        return self._name()


# Et Python-objekt som pakkes inn i QT-objektet MenuWrapper
class MenuItem(object):
    def __init__(self, media, number):
        if isinstance(media, dict):
            self._items = media
            if 'name' in media:
                self.name = media['name']
            elif 'filename' in media:
                self.name = media['filename']
            elif 'title' in media:
                self.name = media['title']
                if 'artist' in media and media['artist']:
                    self.name += '  ' + media['artist']
            elif 'playlist' in media:
                self.name = media['playlist']
            elif 'text' in media:
                self.name = media['text']
            elif 'track' in media:
                self.name = media['track']
            else:
                self.name = str(media)
                
            self.type = media.get('type', '_none')
            
            if 'icon' in media:
                self.thumb = build_img_url(media['icon'])
            elif 'artwork_url' in media:
                self.thumb = build_img_url(media['artwork_url'])
            elif 'image' in media:
                self.thumb = build_img_url(media['image'])
            elif 'coverid' in media:
                self.thumb = build_img_url(
                    'music/{}/cover.jpg'.format(media['coverid']))
            else:
                self.thumb = build_img_url('html/images/newmusic.png')
            
            self.isSearch = ('search' in self.type) and (
                not '_search' in self._items)
            
        else:
            raise Exception("media is not dict")
            
        self.number = number
 
    def __str__(self):
        # return '{} ({})'.format(self.name, self.type)
        return self.name


# En QT-liste av QT-objekter. inni hvert qt-objekt er det et python-objekt
class MediaListModel(QtCore.QAbstractListModel):
    COLUMNS = ('media',)
 
    def __init__(self, medias=[]):
        QtCore.QAbstractListModel.__init__(self)
        self._medias = medias
        self.setRoleNames(dict(enumerate(MediaListModel.COLUMNS)))
 
    def __len__(self):
         return len(self._medias)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._medias)
 
    def data(self, index, role):
        if index.isValid() and role == MediaListModel.COLUMNS.index('media'):
            return self._medias[index.row()]
        return None

    def append(self, media):
        self._medias.append(MenuWrapper(media))

    def extend(self, medialist):
        self._medias.extend([MenuWrapper(media) for media in medialist])
        self.reset() # signal listview to update:
    
    def clear(self):
        self._medias.clear()
        
    def copy_dict(self):
        return self._medias.copy()
