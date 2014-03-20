##[AAFC Soil Tools]=group
##sqliteDbName=string soilDb
##sqliteDbPath=folder
##cmpDbfPath=file
##slfDbfPath=file
##snfDbfPath=file



import os
import sys
import sqlite3

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# aafc module name containing submodules for soil db work
aafc_module_name = "aafc_soil"

# add aafc module name directory to python path. found as .qgis2/processing/scripts/name_of_aafc_module
scriptDirectory = os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), "processing/scripts",aafc_module_name)

# add to python path
sys.path.append(scriptDirectory)

# import aafc_tools
import aafc_utilities as utilities

# create utility class instance
utils = utilities.Utils(iface)


# print user selected field to process
utils.communicateWithUserInQgis("Import of utilities worked")


# remove added aafc soil module from python path
sys.path.pop()
