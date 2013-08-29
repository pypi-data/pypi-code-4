# -*- coding: utf-8 -*-

# image_widgets.py --- Resizable Widgets for displaying images
# Copyright (c) 2011, 2013 Florent Rougon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA.


import logging
from PyQt4 import QtCore, QtGui


def setup_logging(level=logging.NOTSET, chLevel=None):
    global logger

    if chLevel is None:
        chLevel = level

    logger = logging.getLogger('flo_check_homework.image_widgets')
    logger.setLevel(level)
    # Create console handler and set its level
    ch = logging.StreamHandler() # Uses sys.stderr by default
    ch.setLevel(chLevel)  # NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    # Logger name with :%(name)s... many other things available
    formatter = logging.Formatter("%(levelname)s %(message)s")
    # Add formatter to ch
    ch.setFormatter(formatter)
    # Add ch to logger
    logger.addHandler(ch)

setup_logging()


class FixedARLabel(QtGui.QLabel):
    """QLabel subclass that displays an image.

    The widget can be resized and will preserve the aspect ratio of
    the image, filling the remaining space as QLabel normally does
    (similarly as in the Qt screenshot example).

    self.sizeHint() returns the natural size of the image.

    I've tried to create a resizable widget with a fixed aspect ratio
    and no padding, but this is not easy, at least with (Debian) Qt
    4:4.6.3-4+squeeze1.

    At first, sizePolicy.setHeightForWidth(True) seemed like a good
    idea and worked well when the window containing the widget was
    taller than needed for the aspect ratio of the image, because Qt
    obtained a small height from the custom heightForWidth() function
    and managed that easily in the outer layout. However, when the
    outer window was wider than needed, heightForWidth() returned too
    large a number for the height of the window; consequently, the
    label was too tall and clipped by the containing window (as
    documented for QWidget).

    The problem could probably be solved if Qt supported
    widthForHeight() in addition to heightForWidth(), but this is not
    the case at the time of this writing.

    A final attempt was to resize the widget or outer window at
    appropriate times. Resizing the widget gives terrible results
    when it is used in layouts, because these want to have total
    control over the size of the widgets they manage, and don't
    notice when the widgets resize() themselves: this is the layout
    that decides the size of the widgets it manages, possibly taking
    into account their sizeHint() before giving them their geometry
    (except with
    QLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize), which
    doesn't support resizing from the window manager, therefore is
    not of much interest here). Resizing the outer window in its
    resizeEvent more or less works, but causes awful flicker
    (alternating between the size wanted by the window manager/user
    and the size imposed by the subsequent resize() call, with the
    desired aspect ratio).

    Note: the scaledContents property of QLabel doesn't preserve any
          aspect ratio.

    """
    def __init__(self, image, *args, **kwargs):
        """Initialize a FixedARLabel instance.

        'image' must be a QImage. Other arguments are passed to the
        parent constructor.

        QLabel works with QPixmap instances, but scaling a QPixmap is
        done by converting it to a QImage first, scaling the QImage
        and then converting back to a QPixmap (cf.
        QPixmapData::transformed() in src/gui/image/qpixmapdata.cpp).
        Since the scaling may be needed relatively often here, it is
        much faster to start from a single QImage and scale it when
        necessary before converting it to a QPixmap for use by
        QLabel.

        """
        super().__init__(*args, **kwargs)

        # The pixmap will be set after appropriate scaling in the
        # resizeEvent, which will happen before the widget is first
        # shown. Therefore, we can spare a useless self.setPixmap()
        # call here.
        self.origImage = image
        self.origImageSize = image.size() # will be used a lot

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Label)
        # Center the image in the rectangle occupied by the QLabel
        self.setAlignment(QtCore.Qt.AlignCenter)
        # sizePolicy.setHeightForWidth(True) wouldn't work well here,
        # cf. the class docstring.
        self.setSizePolicy(sizePolicy)
        # self.updateGeometry() apparently unnecessary when the size
        # policy is changed in the constructor.

        # The following may be useful for debugging, to see the
        # widget boundaries; it doesn't increase the widget size.
        #
        # self.setFrameStyle(QtGui.QFrame.Panel)
        # self.setLineWidth(2)

    def sizeHint(self):
        # self prefers displaying the image at its natural (unscaled) size if
        # possible.
        return self.origImageSize

    def minimumSizeHint(self):
        s = self.origImage.size() # New object
        # Prevent the widget from becoming really really tiny...
        s.scale(QtCore.QSize(15, 15), QtCore.Qt.KeepAspectRatio)
        return s

    def resizeEvent(self, event):
        size = event.size()     # new size of the widget
        # logger.debug("event.size: %s" % size)

        s = self.origImage.size() # New object
        assert s is not self.origImageSize
        # Biggest rectangle with the same aspect ratio as the image that fits
        # into 'size'.
        s.scale(size, QtCore.Qt.KeepAspectRatio)
        # logger.debug("s: %s" % s)

        delta = size - s
        # We have to tolerate a one pixel difference either in width or in
        # height (exclusive) between 's' and 'size'. This is because if 'size'
        # already has the correct aspect ratio (actually, a good approximation
        # of it), self.origImage.size().scale(size, QtCore.Qt.KeepAspectRatio)
        # will often return a smaller rectangle than 'size': substracting one
        # pixel in width or in height will often give a better approximation
        # of the image aspect ratio (cf. below for a concrete example).
        if delta.width() + delta.height() <= 1:
            s = size
            # logger.debug("delta = %s, using %s as s" % (delta, s))

        # 's' is now the target size for the pixmap, optimal for the new size
        # of the QLabel given the image aspect ratio.

        # Call self.setPixmap() if either the pixmap hasn't been initialized
        # yet or it doesn't have size 's'.
        if not self.pixmap() or s != self.pixmap().size():
            # As explained above, scaling with QtCore.Qt.KeepAspectRatio could
            # yield a pixmap that is smaller by one pixel in width or height
            # than 's'. Since we know 's' has the correct aspect ratio and we
            # want to fill it completely, we use QtCore.Qt.IgnoreAspectRatio.
            #
            # Note: one could obtain faster scaling with
            # QtCore.Qt.FastTransformation, at the expense of quality.
            scaledImage = self.origImage.scaled(s,
                                                  QtCore.Qt.IgnoreAspectRatio,
                                                  QtCore.Qt.SmoothTransformation)
            # logger.debug("scaledImage size: %s" % scaledImage.size())
            self.setPixmap(QtGui.QPixmap.fromImage(scaledImage))

# Example illustrating an important aspect of FixedARLabel.resizeEvent():
#
# >>> from PyQt4 import QtCore, QtGui
# >>> s = QtCore.QSize(1700, 1000)
# >>> s2 = QtCore.QSize(1700, 1000)
# >>> bounds = QtCore.QSize(1024, 768)
# >>> s.scale(bounds, QtCore.Qt.KeepAspectRatio)
# >>> s
# PyQt4.QtCore.QSize(1024, 602)
# >>> s2.scale(s, QtCore.Qt.KeepAspectRatio)
# >>> s2
# PyQt4.QtCore.QSize(1023, 602)
# >>>

class ImageWindow(QtGui.QMainWindow):
    def __init__(self, parent, image, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)

        # Useful when one wants a fixed size main window, the size of which is
        # determined by its contents
        # self.layout().setSizeConstraint(QtGui.QLayout.SetFixedSize)

        self.cWidget = QtGui.QWidget()
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.cWidget.setLayout(self.vLayout)

        self.hLayout = QtGui.QHBoxLayout()
        self.hLayout.setContentsMargins(0, 0, 0, 0)

        self.image = image
        self.setReasonableIcon(self.image)

        self.label = \
            FixedARLabel(self.image)
        self.hLayout.addWidget(self.label)

        self.vLayout.addLayout(self.hLayout)
        self.setCentralWidget(self.cWidget)

        app = QtCore.QCoreApplication.instance()
        assert app is not None, \
            "QtCore.QCoreApplication.instance() returned None"

        desktopWidget = app.desktop()
        # Available space (rectangle) on the desktop; this is really
        # available, for instance, space taken by task bars and various panels
        # doesn't count as available.
        rect = desktopWidget.availableGeometry(self)

        # We want to show the image as big as possible in the available space,
        # unless it is smaller than the available space, and we want to
        # preserve its aspect ratio at all times, even when resized. We don't
        # want any blank space when the window is first shown, therefore its
        # contents must have the same aspect ratio as the image, which can be
        # derived from the FixedARLabel.sizeHint() (which is by design the
        # natural size of the image in pixels).
        sh = self.sizeHint()
        # In order to find the biggest rectangle fitting in
        # desktopWidget.availableGeometry() with the correct aspect ratio and
        # resize the window appropriately, we must take into account the size
        # of window decorations. Unfortunately, at least on X11, this cannot
        # be known until the window is first show()n. As a workaround, we
        # assume the parent window gives the same size for window decorations,
        # which is usually true.
        #
        # Note: the window must be *resized*, because Qt limits the initial
        # size of top-level widgets to 2/3 of the screen's width and height
        # (unless on embedded systems). This is why we can't define the
        # correct initial size as usual in self.sizeHint() (cf. QWidget
        # documentation and kernel/qwidget.cpp in
        # QWidgetPrivate::adjustedSize()).
        bordersSize = self.parent().frameSize() - self.parent().size()
        totalSize = sh + bordersSize

        if totalSize.width() > rect.width() \
                or totalSize.height() > rect.height():
            # Image too big to fit without scaling; let's scale it within the
            # rectangle obtained after removing the size of window decorations
            # from the available space (the argument to QWidget.resize()
            # determines the size of the window *contents*, without
            # considering window decorations).
            remaining = rect.size() - bordersSize
            sh.scale(remaining, QtCore.Qt.KeepAspectRatio)
            self.resize(sh)
        else:
            # The image can be displayed at its natural size in the available
            # space without any scaling; let's do it and override the "2/3 of
            # the screen's width and height" limit mentioned above.
            self.resize(self.sizeHint())

        # Note: the following gives useless results on X11 before the window
        # is shown, at least with (Debian) Qt 4:4.6.3-4+squeeze1.
        #   print "frameSize", self.frameSize()

        # QAction is very convenient to define keyboard shortcuts, even
        # without any associated button or menu item. We just need to add the
        # action to the widget that will handle these shortcuts (here, our
        # QMainWindow).
        closeAction = QtGui.QAction(self.tr("Close"), self)
        closeAction.setShortcuts([QtCore.Qt.Key_Escape, QtCore.Qt.Key_Space,
                                  QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return])
        closeAction.triggered.connect(self.close)
        self.addAction(closeAction)

    # def keyPressEvent(self, event):
    # Imprecise, as it allows many more shortcuts than we want, e.g.,
    # Ctrl-Escape. Better use a QAction that works as expected and can
    # additionally be associated with buttons, menus, etc.
    #     if event.key() in (QtCore.Qt.Key_Escape, QtCore.Qt.Key_Space,
    #                        QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
    #         event.accept()
    #         self.close()
    #     else:
    #         return super().keyPressEvent(event)

    def setReasonableIcon(self, image):
        # QIcon wants a QPixmap, but we don't want to transfer a potentially
        # huge pixmap to the X server for almost no benefit.
        s = image.size()
        maxSize = 128

        if s.width() <= maxSize and s.height() <= maxSize:
            smallImage = image
        else:
            s.scale(maxSize, maxSize, QtCore.Qt.KeepAspectRatio)
            smallImage = image.scaled(s, QtCore.Qt.KeepAspectRatio,
                                      QtCore.Qt.SmoothTransformation)
        icon = QtGui.QIcon(QtGui.QPixmap.fromImage(smallImage))
        self.setWindowIcon(icon)
