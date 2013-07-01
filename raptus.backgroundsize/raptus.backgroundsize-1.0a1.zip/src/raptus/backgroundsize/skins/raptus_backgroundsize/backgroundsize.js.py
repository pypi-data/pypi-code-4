## Script (Python) "backgroundsize.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFCore.utils import getToolByName

props = getToolByName(context, 'portal_properties').site_properties
selectors = props.getProperty('backgroundsize_selectors', ())

if not selectors:
    return ''

return """
    (function($) {

      function init(e) {
        var container = $(this);
        container.find(%s).each(function() {
          var header = $(this);
          var img = new Image();
          img.onload = function() {
            var width = img.width;
            var height = img.height;
            var timer = false;
            img = $('<img src="' + img.src + '">').css({
              'display': 'block',
              'position': 'absolute',
              'max-width': 'none'
            });
            function realign() {
              timer = false;
              var avail_width = header.width();
              var avail_height = header.height();
              var factor = Math.max(avail_width / width, avail_height / height);
              img.css({
                'left': (avail_width - width * factor) / 2,
                'top': (avail_height - height * factor) / 2
              }).attr({
                'width': Math.ceil(width * factor),
                'height': Math.ceil(height * factor)
              });
            }
            realign();
            $(window).resize(function() {
              if(timer)
                return;
              timer = window.setTimeout(realign, 50);
            });
            var wrapper = $('<div />').css({
              'display': 'block',
              'position': 'absolute',
              'top': 0,
              'left': 0,
              'width': '100%%',
              'height': '100%%',
              'overflow': 'hidden'
            }).append(img);
            header.prepend(wrapper).css('background', 'none');
          }
          img.src = header.css('background-image').replace(/url\(['"]([^'"]+)['"]\)/, '$1');
        });
      }

      $(document).ready(function(e) {
        $.proxy(init, $('body'))(e);
        $('.viewletmanager').on('viewlets.updated', init);
      });

    })(jQuery);
""" % ', '.join(selectors)