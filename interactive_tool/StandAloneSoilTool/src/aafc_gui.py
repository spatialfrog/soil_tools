"""
gui related tasks.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


def getFilePathDialog(searchDirectory, filter="dBASE (*.dbf)"):
        """
        present standard qt file dialog. user selects single file.

        returns full file path.
        """

        # TODO: gui -- provide enumeration similar to communicateWithUserInQgis for filter type. only permit dbf & shp

        # get full path to file
        filepath = QFileDialog.getOpenFileNameAndFilter(iface.mainWindow(),"Please choose a file to open...", searchDirectory, filter, "Filter list for selecting files from a dialog box")

        if not len(filepath) == 0:
            # QFileDialog returns tuple of path, filter used
            # only need file path
            return filepath[0]
        else:
            return None


def getUserSettings():
    """
    TODO get user defined config settings ie. add output csv to qgis
    """

    pass


filePath = getFilePathDialog("/Users/drownedfrog/tmp")

if not filePath:
    print "error"
else:
    print filePath
