# -*- coding: utf-8 -*-

# Copyright (C) 2013, David Kuryakin (dkuryakin@gmail.com)
#
# This material is provided "as is", with absolutely no warranty expressed
# or implied. Any use is at your own risk.
#
# Permission to use or copy this software for any purpose is hereby granted
# without fee. Permission to modify the code and to distribute modified
# code is also granted without any restrictions.

import pickle
import sys
import logging
from .features import default_features_list
from .common import page_to_features

logger = logging.getLogger(__name__)

try:
    from PyQt4.QtGui import QApplication, QPainter, QImage
    from PyQt4.QtCore import QUrl, QSize, QTimer, Qt
    from PyQt4.QtWebKit import QWebPage, QWebView
except ImportError:
    logger.error('PyQt4 is not installed! Please, install it if you want to use this library.')
    logger.error('Hint for Ubuntu users (since versoin 12.04): run "sudo apt-get install python-qt4".')
    sys.exit(1)

class Parser(QWebPage):
    def __init__(self,
                 url,
                 features_calculator=default_features_list,
                 useragent='Mozilla/5.0',
                 visible=False,
                 viewport_size=(1600, 1200),
                 show_js_log=True,
                 sleep_after_load=0,  # timeout in seconds, may be float or int
                 screenshot=None,  # None or filename
                 model_file=None
    ):
        self.model = None if model_file is None else pickle.load(open(model_file))
        self.screenshot = screenshot
        self.url = url
        self.useragent = useragent
        self.visible = visible
        self.show_js_log = show_js_log
        self.app = QApplication.instance()
        self.sleep_after_load = sleep_after_load
        self.features_calculator = features_calculator
        if not self.app:
            self.app = QApplication(['constractor.Parser'])

        super(Parser, self).__init__()
        self.setViewportSize(QSize(*viewport_size))
        if visible:
            view = QWebView()
            view.setPage(self)
            view.show()
            view.setFixedSize(*viewport_size)

        self.loadFinished.connect(self._load_finished)
        self.mainFrame().load(QUrl(url))
        self.app.exec_()

    def userAgentForUrl(self, url):
        return self.useragent

    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
        if self.show_js_log:
            msg = "JS LOG: {msg} (line_number={line}, source_id={sid}).".format(
                msg=message, line=lineNumber, sid=sourceID
            )
            logger.debug(msg)

    def _predict(self):
        if self.model is None:
            return
        pred_classes = self.model.predict(self.features)
        self.predicted = []
        for class_id, element in zip(pred_classes, self.context['elements']):
            if not class_id:
                continue
            self.predicted.append(element['element'])

    def _parse(self):
        self.context, self.features = page_to_features(self, self.features_calculator)
        self._predict()

        if self.screenshot is not None:
            self.painter.end()
            self.paint_device.save(self.screenshot)
        self.app.quit()

    def _load_finished(self, result):
        if self.screenshot is not None:
            self.paint_device = QImage(self.mainFrame().contentsSize(), QImage.Format_RGB32)
            self.painter = QPainter(self.paint_device)
            self.mainFrame().render(self.painter)
        QTimer.singleShot(int(self.sleep_after_load * 1000), self._parse)