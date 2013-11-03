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
from .common import page_to_features, train

logger = logging.getLogger(__name__)

try:
    from PyQt4.QtGui import QApplication, QPainter, QImage, QMouseEvent, QMainWindow, \
        QLineEdit, QPushButton, QAction, QLabel, QKeySequence, QMessageBox, QFileDialog
    from PyQt4.QtCore import QUrl, QSize, QTimer, Qt, QObject, QEvent, QPoint
    from PyQt4.QtWebKit import QWebPage, QWebView
except ImportError:
    logger.error('PyQt4 is not installed! Please, install it if you want to use this library.')
    logger.error('Hint for Ubuntu users (since versoin 12.04): run "sudo apt-get install python-qt4".')
    sys.exit(1)

class GuiTrainer(QWebPage):
    CLASS = 'constractor-gui-trainer'
    CLASS_PREDICTED = 'constractor-gui-trainer-predicted'

    def __init__(self,
                 useragent='Mozilla/5.0',
                 viewport_size=(1200, 550),
                 show_js_log=True,
                 except_urls=['yandex', 'google'],
                 features_calculator=default_features_list,
                 save_features=None,
                 save_model=None,
                 train_function=train
    ):
        self.train_function = train_function
        self.features_calculator = features_calculator
        self.except_urls = except_urls
        self.useragent = useragent
        self.show_js_log = show_js_log
        self.app = QApplication.instance()
        self.features = {}
        self.save_features = save_features
        self.save_model = save_model

        if not self.app:
            self.app = QApplication(['constractor.GuiTrainer'])

        class EventFilter(QObject):
            page = self

            def eventFilter(self, receiver, event):
                if event.type() == QEvent.MouseMove:
                    if self.page._bad_url(): return True

                    pos = self.page.view().mapFromGlobal(event.globalPos())
                    res = self.page.mainFrame().hitTestContent(pos)
                    e = res.element()

                    class_name = self.page.CLASS
                    if not e.hasClass(class_name):
                        for ee in self.page.mainFrame().findAllElements('.' + class_name):
                            ee.removeClass(class_name)
                        e.addClass(class_name)

                    return True
                else:
                    return super(EventFilter, self).eventFilter(receiver, event)

        efilter = EventFilter()
        self.app.installEventFilter(efilter)

        super(GuiTrainer, self).__init__()
        self.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.setViewportSize(QSize(*viewport_size))

        wnd = QMainWindow()

        view = QWebView(wnd)
        view.setPage(self)
        view.setFixedSize(*viewport_size)

        wnd.setWindowTitle('constractor.GuiTrainer')
        wnd.setFixedSize(viewport_size[0], viewport_size[1] + 90)
        wnd.setCentralWidget(view)

        yandex = QAction('Go Yandex', self)
        yandex.setShortcut('Ctrl+Y')
        yandex.setStatusTip('Load Yandex')
        yandex.triggered.connect(self._go_yandex)

        google = QAction('Go Google', self)
        google.setShortcut('Ctrl+G')
        google.setStatusTip('Load Google')
        google.triggered.connect(self._go_google)

        save_features = QAction('Save features', self)
        save_features.setShortcut('Ctrl+F')
        save_features.setStatusTip('Save features')
        save_features.triggered.connect(self._save_features)

        train = QAction('Train', self)
        train.setShortcut('Ctrl+T')
        train.setStatusTip('Train')
        train.triggered.connect(self._train)

        predict = QAction('Predict', self)
        predict.setShortcut('Ctrl+P')
        predict.setStatusTip('Predict')
        predict.triggered.connect(self._predict)

        save_model = QAction('Save model', self)
        save_model.setShortcut('Ctrl+M')
        save_model.setStatusTip('Save model')
        save_model.triggered.connect(self._save_model)

        open_features = QAction('Open features', self)
        open_features.setShortcut('Ctrl+L')
        open_features.setStatusTip('Open features')
        open_features.triggered.connect(self._open_features)

        open_model = QAction('Open model', self)
        open_model.setShortcut('Ctrl+O')
        open_model.setStatusTip('Open model')
        open_model.triggered.connect(self._open_model)

        select = QAction('Choose selected', self)
        select.setShortcut('Ctrl+S')
        select.setStatusTip('Choose selected')
        select.triggered.connect(self._featurize)

        goback = QAction('Go back', self)
        goback.setShortcut('Ctrl+B')
        goback.setStatusTip('Go back')
        goback.triggered.connect(self.view().back)

        reset = QAction('Reset', self)
        reset.setShortcut('Ctrl+R')
        reset.setStatusTip('Reset features & model')
        reset.triggered.connect(self._reset)

        _exit = QAction('Exit', self)
        _exit.setShortcut('Ctrl+X')
        _exit.setStatusTip('Exit')
        _exit.triggered.connect(wnd.close)

        menubar1 = wnd.menuBar()
        file = menubar1.addMenu('&File')
        file.addAction(save_features)
        file.addAction(save_model)
        file.addAction(open_features)
        file.addAction(open_model)
        file.addAction(_exit)

        menubar2 = wnd.menuBar()
        file = menubar2.addMenu('&Browser')
        file.addAction(yandex)
        file.addAction(google)
        file.addAction(goback)

        menubar3 = wnd.menuBar()
        file = menubar3.addMenu('&Machine Learning')
        file.addAction(select)
        file.addAction(train)
        file.addAction(predict)
        file.addAction(reset)

        toolbar = wnd.addToolBar('toolbar')
        toolbar.setFixedHeight(40)

        address = QLineEdit(toolbar)
        address.setGeometry(10, 5, viewport_size[0] - 20, 30)
        address.returnPressed.connect(self._set_addr)
        self.address = address

        wnd.statusBar().showMessage('Application was started.')

        wnd.show()
        self.main_window = wnd
        self.event_count = 0

        self.loadStarted.connect(self._load_started)
        self.loadFinished.connect(self._load_finished)
        self.linkClicked.connect(self._link_clicked)
        self.app.exec_()

    def _reset(self):
        self.features = {}
        if hasattr(self, 'classifier'):
            delattr(self, 'classifier')

    def _features(self):
        _classes = []
        _features = []
        for key, features_class in self.features.iteritems():
            for features, class_id in features_class:
                _classes.append(class_id)
                _features.append(features)
        return _classes, _features

    def _train(self):
        _classes, _features = self._features()
        if len(set(_classes)) < 2:
            self.main_window.statusBar().showMessage(
                'Event #{event}: there is less than 2 classes presented in train sampling. Don\'t forget use Ctrl+S!'.format(event=self.event_count)
            )
            self.event_count += 1
            return

        result, classifier = train(_classes, _features)
        self.main_window.statusBar().showMessage(
            'Event #{event}: classifier was trained. Accuracy is {acc}.'.format(event=self.event_count, acc=result)
        )
        self.event_count += 1
        self.classifier = classifier

    def _predict(self):
        if not hasattr(self, 'classifier'):
            self.main_window.statusBar().showMessage(
                'Event #{event}: there is no classifier to predict. Train first.'.format(event=self.event_count)
            )
            self.event_count += 1
            return
        context, features = page_to_features(self, self.features_calculator)
        predictions = self.classifier.predict(features)
        element_prediction = zip(context['elements'], predictions)
        for element, prediction in element_prediction:
            element = element['element']
            if element.hasClass(self.CLASS_PREDICTED) and not prediction:
                element.removeClass(self.CLASS_PREDICTED)
            if prediction:
                element.addClass(self.CLASS_PREDICTED)

    def _save_features(self):
        if self.save_features is None:
            save_features = QFileDialog.getOpenFileName(self.main_window, 'Open file')
        else:
            save_features = self.save_features

        try:
            with open(save_features, 'w') as f:
                for key, features_class in self.features.iteritems():
                    for features, class_id in features_class:
                        print >> f, '\t'.join(map(str, [class_id] + list(features)))
        except:
            self.main_window.statusBar().showMessage(
                'Event #{event}: unable to save features!'.format(event=self.event_count)
            )
            self.event_count += 1
            raise

        self.main_window.statusBar().showMessage(
            'Event #{event}: features were saved.'.format(event=self.event_count)
        )
        self.event_count += 1


    def _save_model(self):
        if self.save_model is None:
            save_model = QFileDialog.getOpenFileName(self.main_window, 'Open file')
        else:
            save_model = self.save_model

        if not hasattr(self, 'classifier'):
            self.main_window.statusBar().showMessage(
                'Event #{event}: there is no classifier to predict. Train first.'.format(event=self.event_count)
            )
            self.event_count += 1
            return
        try:
            with open(save_model, 'w') as f:
                pickle.dump(self.classifier, f)
        except:
            self.main_window.statusBar().showMessage(
                'Event #{event}: unable to save model!'.format(event=self.event_count)
            )
            self.event_count += 1
            raise

        self.main_window.statusBar().showMessage(
            'Event #{event}: model was saved.'.format(event=self.event_count)
        )
        self.event_count += 1


    def _open_features(self):
        if self.save_features is None:
            open_features = QFileDialog.getOpenFileName(self.main_window, 'Open file')
        else:
            open_features = self.save_features

        try:
            _features = []
            with open(open_features) as f:
                for l in f:
                    l = l.strip()
                    if not l: continue
                    fields = l.split('\t')
                    class_id = int(fields.pop(0))
                    features = map(float, fields)
                    _features.append((features, class_id))
            self.features = {'__constractor.loaded.features__': _features}
        except:
            self.main_window.statusBar().showMessage(
                'Event #{event}: unable to load features!'.format(event=self.event_count)
            )
            self.event_count += 1
            raise

        self.main_window.statusBar().showMessage(
            'Event #{event}: features were loaded.'.format(event=self.event_count)
        )
        self.event_count += 1

    def _open_model(self):
        if self.save_model is None:
            open_model = QFileDialog.getOpenFileName(self.main_window, 'Open file')
        else:
            open_model = self.save_model

        try:
            with open(open_model) as f:
                self.classifier = pickle.load(f)
        except:
            self.main_window.statusBar().showMessage(
                'Event #{event}: unable to load model!'.format(event=self.event_count)
            )
            self.event_count += 1
            raise

        self.main_window.statusBar().showMessage(
            'Event #{event}: model was loaded.'.format(event=self.event_count)
        )
        self.event_count += 1

    def _bad_url(self):
        url = unicode(self.mainFrame().url().toString())
        if not url: return True
        for eurl in self.except_urls:
            if eurl in url: return True
        return False

    def _featurize(self):
        if self._bad_url(): return
        url = unicode(self.mainFrame().url().toString())
        context, features = page_to_features(self, self.features_calculator)
        element_features = zip(context['elements'], features)
        self.features[url] = []
        targets = 0
        for element, features in element_features:
            is_target = element['element'].hasClass(self.CLASS)
            self.features[url].append((features, int(is_target)))
            if is_target: targets += 1
        self.main_window.statusBar().showMessage(
            'Event #{event}: features for were calculated. There is {target} target from {tot} items.'.format(
                target=targets, tot=len(element_features), event=self.event_count
            )
        )
        self.event_count += 1

    def _link_clicked(self, url):
        self.mainFrame().load(url)

    def _set_addr(self, address=None):
        if isinstance(address, QUrl):
            address = unicode(address.toString())
        url = unicode(self.address.text() if address is None else address)
        if u'://' not in url:
            url = u'http://' + url
        self.mainFrame().load(QUrl(url))

    def _go_yandex(self):
        self._set_addr('yandex.ru')

    def _go_google(self):
        self._set_addr('google.com')

    def userAgentForUrl(self, url):
        return self.useragent

    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
        if self.show_js_log:
            msg = "JS LOG: {msg} (line_number={line}, source_id={sid}).".format(
                msg=message, line=lineNumber, sid=sourceID
            )
            logger.debug(msg)

    def _inject_js(self):
        self.mainFrame().evaluateJavaScript('''
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = '.%s { background: #000; } .%s { background: #F00; }';
            document.querySelector('head').appendChild(style);
        ''' % (self.CLASS, self.CLASS_PREDICTED))

    def _load_started(self, *args, **kwargs):
        self.address.setText('')

    def _load_finished(self, result):
        self.address.setText(self.mainFrame().url().toString())
        self._inject_js()