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
        filepath,filter = QFileDialog.getOpenFileNameAndFilter(iface.mainWindow(),"Please choose a file to open...", searchDirectory, filter, "Filter list for selecting files from a dialog box")

        if len(filepath) == 0:
            return None
        else:
            print "error"
            #self.communicateWithUserInQgis(filepath)
            return filepath


def getUserSettings():
    """
    TODO get user defined config settings ie. add output csv to qgis
    """

    pass


getFilePathDialog("/Users/drownedfrog/tmp")