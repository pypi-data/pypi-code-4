# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/pydosh.ui'
#
# Created: Wed Mar 20 15:04:02 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_pydosh(object):
    def setupUi(self, pydosh):
        pydosh.setObjectName(_fromUtf8("pydosh"))
        pydosh.resize(1042, 666)
        self.centralwidget = QtGui.QWidget(pydosh)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_4 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.widget_3 = QtGui.QWidget(self.centralwidget)
        self.widget_3.setObjectName(_fromUtf8("widget_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.widget_3)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox = QtGui.QGroupBox(self.widget_3)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.checkedCombo = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkedCombo.sizePolicy().hasHeightForWidth())
        self.checkedCombo.setSizePolicy(sizePolicy)
        self.checkedCombo.setObjectName(_fromUtf8("checkedCombo"))
        self.gridLayout.addWidget(self.checkedCombo, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.accountCombo = MultiComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accountCombo.sizePolicy().hasHeightForWidth())
        self.accountCombo.setSizePolicy(sizePolicy)
        self.accountCombo.setObjectName(_fromUtf8("accountCombo"))
        self.gridLayout.addWidget(self.accountCombo, 2, 1, 1, 1)
        self.inoutCombo = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inoutCombo.sizePolicy().hasHeightForWidth())
        self.inoutCombo.setSizePolicy(sizePolicy)
        self.inoutCombo.setObjectName(_fromUtf8("inoutCombo"))
        self.gridLayout.addWidget(self.inoutCombo, 1, 1, 1, 1)
        self.label_13 = QtGui.QLabel(self.groupBox)
        self.label_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout.addWidget(self.label_13, 1, 0, 1, 1)
        self.label_14 = QtGui.QLabel(self.groupBox)
        self.label_14.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_14.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout.addWidget(self.label_14, 0, 2, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 2, 2, 1, 1)
        self.amountEdit = SearchLineEdit(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.amountEdit.sizePolicy().hasHeightForWidth())
        self.amountEdit.setSizePolicy(sizePolicy)
        self.amountEdit.setObjectName(_fromUtf8("amountEdit"))
        self.gridLayout.addWidget(self.amountEdit, 1, 3, 1, 1)
        self.descEdit = SearchLineEdit(self.groupBox)
        self.descEdit.setObjectName(_fromUtf8("descEdit"))
        self.gridLayout.addWidget(self.descEdit, 0, 3, 1, 1)
        self.tagCombo = MultiComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tagCombo.sizePolicy().hasHeightForWidth())
        self.tagCombo.setSizePolicy(sizePolicy)
        self.tagCombo.setObjectName(_fromUtf8("tagCombo"))
        self.gridLayout.addWidget(self.tagCombo, 2, 3, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 2, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.widget_3)
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setCheckable(False)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_5.addWidget(self.label, 0, 0, 1, 1)
        self.endDateEdit = QtGui.QDateEdit(self.groupBox_2)
        self.endDateEdit.setObjectName(_fromUtf8("endDateEdit"))
        self.gridLayout_5.addWidget(self.endDateEdit, 0, 1, 1, 2)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_5.addWidget(self.label_2, 1, 0, 1, 1)
        self.startDateEdit = QtGui.QDateEdit(self.groupBox_2)
        self.startDateEdit.setObjectName(_fromUtf8("startDateEdit"))
        self.gridLayout_5.addWidget(self.startDateEdit, 1, 1, 1, 2)
        self.dateCombo = QtGui.QComboBox(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateCombo.sizePolicy().hasHeightForWidth())
        self.dateCombo.setSizePolicy(sizePolicy)
        self.dateCombo.setObjectName(_fromUtf8("dateCombo"))
        self.gridLayout_5.addWidget(self.dateCombo, 2, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 3, 1, 1)
        self.gridLayout_4.addWidget(self.widget_3, 0, 0, 1, 1)
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.toggleCheckButton = QtGui.QToolButton(self.widget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/accept.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toggleCheckButton.setIcon(icon)
        self.toggleCheckButton.setObjectName(_fromUtf8("toggleCheckButton"))
        self.horizontalLayout_2.addWidget(self.toggleCheckButton)
        self.tagEditButton = QtGui.QToolButton(self.widget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/tag_yellow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tagEditButton.setIcon(icon1)
        self.tagEditButton.setObjectName(_fromUtf8("tagEditButton"))
        self.horizontalLayout_2.addWidget(self.tagEditButton)
        self.reloadButton = QtGui.QToolButton(self.widget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/arrow_refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reloadButton.setIcon(icon2)
        self.reloadButton.setObjectName(_fromUtf8("reloadButton"))
        self.horizontalLayout_2.addWidget(self.reloadButton)
        self.deleteButton = QtGui.QToolButton(self.widget)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/cross.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteButton.setIcon(icon3)
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout_2.addWidget(self.deleteButton)
        spacerItem1 = QtGui.QSpacerItem(703, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout_4.addWidget(self.widget, 1, 0, 1, 1)
        self.widget_2 = QtGui.QWidget(self.centralwidget)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.connectionStatusText = QtGui.QLabel(self.widget_2)
        self.connectionStatusText.setObjectName(_fromUtf8("connectionStatusText"))
        self.horizontalLayout_3.addWidget(self.connectionStatusText)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.label_10 = QtGui.QLabel(self.widget_2)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_3.addWidget(self.label_10)
        self.inTotalLabel = QtGui.QLabel(self.widget_2)
        self.inTotalLabel.setObjectName(_fromUtf8("inTotalLabel"))
        self.horizontalLayout_3.addWidget(self.inTotalLabel)
        spacerItem3 = QtGui.QSpacerItem(28, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.label_11 = QtGui.QLabel(self.widget_2)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_3.addWidget(self.label_11)
        self.outTotalLabel = QtGui.QLabel(self.widget_2)
        self.outTotalLabel.setObjectName(_fromUtf8("outTotalLabel"))
        self.horizontalLayout_3.addWidget(self.outTotalLabel)
        spacerItem4 = QtGui.QSpacerItem(134, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.label_12 = QtGui.QLabel(self.widget_2)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_3.addWidget(self.label_12)
        self.recordCountLabel = QtGui.QLabel(self.widget_2)
        self.recordCountLabel.setObjectName(_fromUtf8("recordCountLabel"))
        self.horizontalLayout_3.addWidget(self.recordCountLabel)
        self.gridLayout_4.addWidget(self.widget_2, 3, 0, 1, 1)
        self.widget_4 = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_4.sizePolicy().hasHeightForWidth())
        self.widget_4.setSizePolicy(sizePolicy)
        self.widget_4.setObjectName(_fromUtf8("widget_4"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget_4)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tableView = QtGui.QTableView(self.widget_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.horizontalLayout.addWidget(self.tableView)
        self.widget_5 = QtGui.QWidget(self.widget_4)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy)
        self.widget_5.setObjectName(_fromUtf8("widget_5"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget_5)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem5 = QtGui.QSpacerItem(20, 108, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem5)
        self.tagView = TagTableView(self.widget_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tagView.sizePolicy().hasHeightForWidth())
        self.tagView.setSizePolicy(sizePolicy)
        self.tagView.setFrameShape(QtGui.QFrame.NoFrame)
        self.tagView.setObjectName(_fromUtf8("tagView"))
        self.verticalLayout.addWidget(self.tagView)
        spacerItem6 = QtGui.QSpacerItem(20, 108, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)
        self.horizontalLayout.addWidget(self.widget_5)
        self.gridLayout_4.addWidget(self.widget_4, 2, 0, 1, 1)
        pydosh.setCentralWidget(self.centralwidget)
        self.label_14.setBuddy(self.descEdit)
        self.label_6.setBuddy(self.amountEdit)

        self.retranslateUi(pydosh)
        QtCore.QMetaObject.connectSlotsByName(pydosh)

    def retranslateUi(self, pydosh):
        pydosh.setWindowTitle(QtGui.QApplication.translate("pydosh", "pydosh", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("pydosh", "filter", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("pydosh", "checked", None, QtGui.QApplication.UnicodeUTF8))
        self.checkedCombo.setToolTip(QtGui.QApplication.translate("pydosh", "filter on checked status", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("pydosh", "account", None, QtGui.QApplication.UnicodeUTF8))
        self.accountCombo.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>filter on account type</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.inoutCombo.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>filter on money in or out</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("pydosh", "in/out", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("pydosh", "&description", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("pydosh", "&amount", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("pydosh", "tag", None, QtGui.QApplication.UnicodeUTF8))
        self.amountEdit.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>filter by amount (Alt-a)</p><p>Accepts operators = &gt; &gt;= &lt; &lt;=</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.descEdit.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>filter on description (Alt-d)</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tagCombo.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>filter on tags</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("pydosh", "date", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("pydosh", "end", None, QtGui.QApplication.UnicodeUTF8))
        self.endDateEdit.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>Set the end date filter</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("pydosh", "start", None, QtGui.QApplication.UnicodeUTF8))
        self.startDateEdit.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>Set the start date filter</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.dateCombo.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>Select a date filter</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.toggleCheckButton.setToolTip(QtGui.QApplication.translate("pydosh", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Arial\'; font-size:10pt;\">toggle checked</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.toggleCheckButton.setText(QtGui.QApplication.translate("pydosh", "&t", None, QtGui.QApplication.UnicodeUTF8))
        self.tagEditButton.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>edit tags</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tagEditButton.setText(QtGui.QApplication.translate("pydosh", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadButton.setToolTip(QtGui.QApplication.translate("pydosh", "reload data (Alt-r)", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadButton.setText(QtGui.QApplication.translate("pydosh", "&r", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setToolTip(QtGui.QApplication.translate("pydosh", "<html><head/><body><p>delete record(s)</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setText(QtGui.QApplication.translate("pydosh", "&r", None, QtGui.QApplication.UnicodeUTF8))
        self.connectionStatusText.setText(QtGui.QApplication.translate("pydosh", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("pydosh", "in:", None, QtGui.QApplication.UnicodeUTF8))
        self.inTotalLabel.setToolTip(QtGui.QApplication.translate("pydosh", "total incoming for filtered records", None, QtGui.QApplication.UnicodeUTF8))
        self.inTotalLabel.setText(QtGui.QApplication.translate("pydosh", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("pydosh", "out:", None, QtGui.QApplication.UnicodeUTF8))
        self.outTotalLabel.setToolTip(QtGui.QApplication.translate("pydosh", "total outgoing for filtered records", None, QtGui.QApplication.UnicodeUTF8))
        self.outTotalLabel.setText(QtGui.QApplication.translate("pydosh", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("pydosh", "showing:", None, QtGui.QApplication.UnicodeUTF8))
        self.recordCountLabel.setToolTip(QtGui.QApplication.translate("pydosh", "filtered records / total records", None, QtGui.QApplication.UnicodeUTF8))
        self.recordCountLabel.setText(QtGui.QApplication.translate("pydosh", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

from searchlineedit import SearchLineEdit
from multicombobox import MultiComboBox
from views import TagTableView
import pydosh_rc
