# Copyright (C) 2012 Vaadin Ltd. 
# Copyright (C) 2012 Richard Lincoln
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.

from muntjac.addon.google_maps.overlay.poly_overlay \
    import PolyOverlay


class Polygon(PolyOverlay):

    def __init__(self, Id, points, strokeColor='#ffffff', strokeWeight=1,
                strokeOpacity=1.0, fillColor='#777777', fillOpacity=0.2,
                clickable=False):
        super(Polygon, self).__init__(Id, points, strokeColor, strokeWeight,
                strokeOpacity, clickable)
        self._fillColor = fillColor
        self._fillOpacity = fillOpacity


    def getFillColor(self):
        return self._fillColor


    def setFillColor(self, fillColor):
        self._fillColor = fillColor


    def getFillOpacity(self):
        return self._fillOpacity


    def setFillOpacity(self, fillOpacity):
        self._fillOpacity = fillOpacity
