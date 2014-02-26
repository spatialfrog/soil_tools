# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_aafcqgissoiltool.ui'
#
# Created: Sat Feb  8 11:37:42 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_AafcQgisSoilTool(object):
    def setupUi(self, AafcQgisSoilTool):
        AafcQgisSoilTool.setObjectName(_fromUtf8("AafcQgisSoilTool"))
        AafcQgisSoilTool.resize(379, 282)
        self.buttonBox = QtGui.QDialogButtonBox(AafcQgisSoilTool)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.getDbfHeaders = QtGui.QPushButton(AafcQgisSoilTool)
        self.getDbfHeaders.setGeometry(QtCore.QRect(30, 30, 141, 32))
        self.getDbfHeaders.setFlat(False)
        self.getDbfHeaders.setObjectName(_fromUtf8("getDbfHeaders"))
        self.label = QtGui.QLabel(AafcQgisSoilTool)
        self.label.setGeometry(QtCore.QRect(30, 10, 131, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(AafcQgisSoilTool)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AafcQgisSoilTool.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AafcQgisSoilTool.reject)
        QtCore.QObject.connect(self.getDbfHeaders, QtCore.SIGNAL(_fromUtf8("clicked()")), AafcQgisSoilTool.accept)
        QtCore.QMetaObject.connectSlotsByName(AafcQgisSoilTool)

    def retranslateUi(self, AafcQgisSoilTool):
        AafcQgisSoilTool.setWindowTitle(_translate("AafcQgisSoilTool", "AafcQgisSoilTool", None))
        self.getDbfHeaders.setToolTip(_translate("AafcQgisSoilTool", "Open the cmp dbf on file system", None))
        self.getDbfHeaders.setText(_translate("AafcQgisSoilTool", "Get Field Headers", None))
        self.label.setText(_translate("AafcQgisSoilTool", "Get dbf field headers", None))

