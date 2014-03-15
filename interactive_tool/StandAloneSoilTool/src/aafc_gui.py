"""
#TODO: gui -- update doc string
gui related tasks.

"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


def getFilePathFromDialog(searchDirectory, filter="dBASE (*.dbf)"):
        """
        purpose:
        allow user to select file from computer for use in script
        
        how:
        pyqt4
        
        notes:
        filter is used by script to modify what user may search for
        
        returns:
        full path to file
        """

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


filePath = getFilePathFromDialog("/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test", filter="Document (*.sqlite)")

if not filePath:
    print "error"
else:
    print filePath
