#!/usr/bin/env python
'''
slipmap based on cuav_tile
'''

import cuav_util, cuav_tile, math

class CUAVSlipMap():
    '''
    a generic image viewer widget for use in CUAV tools
    '''
    def __init__(self,
                 title='SlipMap',
                 lat=-35.0,
                 lon=149.0,
                 width=512,
                 height=512,
                 ground_width=1000,
                 download=True):
        import multiprocessing

        self.ct = cuav_tile.cuavTile(download=download)
        self.lat = lat
        self.lon = lon
        self.width = width
        self.height = height
        self.ground_width = ground_width

        self.drag_step = 10

        self.title = title
        self.parent_pipe,self.child_pipe = multiprocessing.Pipe()
        self.close_window = multiprocessing.Event()
        self.close_window.clear()
        self.child = multiprocessing.Process(target=self.child_task)
        self.child.start()


    def child_task(self):
        '''child process - this holds all the GUI elements'''
        import wx, matplotlib
        matplotlib.use('WXAgg')
        self.app = wx.PySimpleApp()
        self.app.frame = CUAVSlipMapFrame(state=self)
        self.app.frame.Show()
        self.app.MainLoop()

    def close(self):
        '''close the window'''
        self.close_window.set()
        if self.is_alive():
            self.child.join(2)

    def is_alive(self):
        '''check if graph is still going'''
        return self.child.is_alive()

import wx
from PIL import Image

class CUAVSlipMapFrame(wx.Frame):
    """ The main frame of the viewer
    """    
    def __init__(self, state):
        wx.Frame.__init__(self, None, wx.ID_ANY, state.title)
        self.state = state
        state.frame = self
        state.panel = CUAVSlipMapPanel(self, state)
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.Bind(wx.EVT_SIZE, state.panel.on_size)
        
    def on_idle(self, event):
        '''prevent the main loop spinning too fast'''
        import time
        time.sleep(0.1)

class ImagePanel(wx.Panel):
    '''a resizable panel containing an image'''
    def __init__(self, parent, img):
        wx.Panel.__init__(self, parent, -1, size=(1, 1))
        self.set_image(img)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        
    def on_paint(self, event):
        '''repaint the image'''
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(self._bmp, 0, 0)

    def set_image(self, img):
        self._bmp = wx.BitmapFromImage(img)
        self.SetMinSize((self._bmp.GetWidth(), self._bmp.GetHeight()))


class CUAVSlipMapPanel(wx.Panel):
    """ The image panel
    """    
    def __init__(self, parent, state):
        wx.Panel.__init__(self, parent)
        self.state = state
        self.img = None
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.redraw_timer.Start(1000)
        self.create_main_window()
        self.mouse_down = None
        self.imagePanel = ImagePanel(self, wx.EmptyImage(state.width,state.height))
        self.mainSizer.Add(self.imagePanel, 0, wx.ALL|wx.CENTER, 5)
        self.imagePanel.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.imagePanel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.imagePanel.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.last_view = None
        self.redraw_map()

    def on_focus(self, event):
        state = self.state
        state.panel.imagePanel.SetFocus()

    def create_main_window(self):
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)

    def current_view(self):
        '''return a tuple representing the current view'''
        state = self.state
        return (state.lat, state.lon, state.width, state.height,
                state.ground_width, state.ct.tiles_pending())

    def redraw_map(self):
        '''redraw the map with current settings'''
        state = self.state
        if self.last_view and self.last_view == self.current_view():
            return
        state.ground_width = max(state.ground_width, 20)
        state.ground_width = min(state.ground_width, 20000000)
        img = state.ct.area_to_image(state.lat, state.lon, state.width, state.height, state.ground_width)
        self.img = wx.EmptyImage(state.width,state.height)
        self.img.SetData(img.tostring())
        self.imagePanel.set_image(self.img)
        self.mainSizer.Fit(self)
        self.mainSizer.Layout()
        self.Refresh()
        self.last_view = self.current_view()
        self.SetFocus()
        
    def on_redraw_timer(self, event):
        state = self.state
        self.redraw_map()

    def on_size(self, event):
        '''handle window size changes'''
        state = self.state
        size = event.GetSize()
        state.width = size.width
        state.height = size.height
        self.redraw_map()

    def on_mouse_wheel(self, event):
        '''handle mouse wheel zoom changes'''
        state = self.state
        rotation = event.GetWheelRotation() / event.GetWheelDelta()
        if rotation > 0:
            state.ground_width /= 1.1 * rotation
        elif rotation < 0:
            state.ground_width *= 1.1 * (-rotation)
        self.redraw_map()

    def on_mouse(self, event):
        '''handle mouse events'''
        state = self.state
        if event.LeftDown():
            self.mouse_down = event.GetPosition()
        if event.Dragging() and self.mouse_down is not None:
            newpos = event.GetPosition()
            dx = (self.mouse_down.x - newpos.x)
            dy = -(self.mouse_down.y - newpos.y)
            pdist = math.sqrt(dx**2 + dy**2)
            if pdist > state.drag_step:
                bearing = math.degrees(math.atan2(dx, dy))
                distance = (state.ground_width/float(state.width)) * pdist
                newlatlon = cuav_util.gps_newpos(state.lat, state.lon, bearing, distance)
                (state.lat, state.lon) = newlatlon
                self.mouse_down = newpos
                self.redraw_map()

    def on_key_down(self, event):
        '''handle keyboard input'''
        state = self.state
        c = event.GetUniChar()
        if c == ord('=') and event.ShiftDown():
            state.ground_width /= 1.2
            event.Skip()
        elif c == ord('+'):
            state.ground_width /= 1.2
            event.Skip()
        elif c == ord('-'):
            state.ground_width *= 1.2
            event.Skip()


            
if __name__ == "__main__":
    import time
    
    sm = CUAVSlipMap(download=True)
    while sm.is_alive():
        time.sleep(0.1)
