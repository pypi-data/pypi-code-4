#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import os
from uuid import uuid4
from formv.utils.compat import PY2, PY3
if PY2:
    import Image, ImageEnhance, ImageDraw
if PY3:
    try:
        import Image, ImageEnhance, ImageDraw
    except ImportError:        
        from PIL import Image, ImageEnhance, ImageDraw

__all__ = ('imprint','text_to_image','watermark',)

def _imprint(img, text, font=None, color=(0,0,0,255), float='top-left', 
             margin=(0,0), opacity=1, angle=None):    
    assert float in ('top-left','top-center','top-right',
                     'center-left','center','center-right',
                     'bottom-left','bottom-center','bottom-right')    
    
    textlayer = Image.new("RGBA", img.size, (0,0,0,0)) # - transparent layer
    textdraw = ImageDraw.Draw(textlayer) 
    textsize = textdraw.textsize(text, font)

    x = {'left': margin[0], 
         'center': (img.size[0]-textsize[0])/2,
         'right': img.size[0]-textsize[0]-margin[0]}
    y = {'top': margin[1],
         'center': (img.size[1]-textsize[1])/2,
         'bottom': img.size[1]-textsize[1]-margin[1]}    
    
    y_pos, x_pos = (('center','center') 
                    if float=='center' else float.split('-'))
    textpos = (x[x_pos], y[y_pos])
    textdraw.text(textpos, text, font=font, fill=color)
    if opacity != 1: 
        textlayer = _reduce_opacity(textlayer, opacity)
    if angle:
        textlayer = textlayer.rotate(angle, expand=False)  
    
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    layer.paste(textlayer, (0,0))
    return Image.composite(layer, img, layer)


def _reduce_opacity(img, opacity):
    assert 0 <= opacity <= 1
    img = img.convert('RGBA') if img.mode != 'RGBA' else img.copy() 
    alpha = img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    img.putalpha(alpha)
    return img


def text_to_image(text, dir_path, image_size, image_format='PNG',  
                  bgcolor=(255,255,255,255), font=None, 
                  color=None, float='center-left', margin=(5,0)):    
    img = Image.new("RGBA", image_size, bgcolor)
    img = _imprint(img=img, text=text, font=font, color=color, 
                   float=float, margin=margin, opacity=1)    
    image_name = str(uuid4()).replace('-','')+'.'+image_format.lower() 
    image_path = os.path.join(dir_path, image_name) 
    img.save(image_path, image_format)
    return image_path


def watermark(image_path, type='text', mode='tile', text=None, 
              layer=(160,120), font=None, color=(0,0,0,255), 
              file=None, margin=(0,0), opacity=.3, angle=None):
    if type == 'text':
        img = Image.new("RGBA", layer, (0,0,0,0))      
        wmark = _imprint(img, text=text, font=font, color=color, float='center')
    elif type == 'image':
        wmark = Image.open(file)
        
    if opacity < 1:
        wmark = _reduce_opacity(wmark, opacity)
    
    if angle:
        wmark = wmark.rotate(angle, expand=False)  
        
    img = Image.open(image_path)

    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    if mode == 'tile':
        for y in range(0, img.size[1], wmark.size[1]):
            for x in range(0, img.size[0], wmark.size[0]):
                layer.paste(wmark, (x, y))
    elif mode == 'scale':
        ratio = min(float(img.size[0]) / wmark.size[0], 
                    float(img.size[1]) / wmark.size[1])
        w = int(wmark.size[0] * ratio)
        h = int(wmark.size[1] * ratio)
        wmark = wmark.resize((w, h))
        layer.paste(wmark, ((img.size[0]-w)/2, (img.size[1]-h)/2))
    elif mode == 'fixed':
        layer.paste(wmark, margin)
    img = Image.composite(layer, img, layer)
    img.save(image_path)


def imprint(image_path, text, font=None, color=None, float='bottom-right', 
            margin=(25,25), opacity=1, angle=None):    
    img = Image.open(image_path)
    img = _imprint(img=img, text=text, font=font, color=color, 
                   float=float, margin=margin, opacity=opacity,
                   angle=angle)
    img.save(image_path)