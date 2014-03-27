# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AafcQgisSoilToolDialog
                                 A QGIS plugin
 Tools allows interaction with Canadian soli databases hosted on Cansis website
                             -------------------
        begin                : 2014-02-05
        copyright            : (C) 2014 by richard burcher
        email                : richardburcher@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_aafcqgissoiltool import Ui_AafcQgisSoilTool
# create the dialog for zoom to point


class AafcQgisSoilToolDialog(QtGui.QDialog, Ui_AafcQgisSoilTool):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
