"""
purpose:
loads the database table "availableSoilTableJoins", cmp table if selected and slc shapefile

notes:
- loads "permittedOperations" table into qgis toc. becomes drop down in processing framework for next script. will allows user to specific what tables
they wish to use and if a join operation is required
- loading the slc shapefile is required. user could load via standard qgis interface tools
- user can select to load cmp table if this is the table they wish to work with

input:
db must have been created

output:
loads db table "availableSoilTableJoins" into qgis canvas

license:
- gpl3

by:
richard burcher
richardburcher@gmail.com
2014
"""

#==========
# sets up gui in qgis processing framework
##[AAFC Soil Tools]=group
##soil_database=file
##slc_shapefile=vector
#===========

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import os
import sys
import sqlite3


# aafc module name containing submodules for soil db work
aafcModuleName = "aafc_modules"

# add aafc module name directory to python path. found as .qgis2/processing/scripts/name_of_aafc_module
scriptDirectory = os.path.join(QFileInfo(QgsApplication.qgisUserDbFilePath()).path(), "processing/scripts",aafcModuleName)

# add to aafc module directory to python path
sys.path.append(scriptDirectory)

# import aafc_modules
import aafc_utilities as utilities
import aafc_database as database

# create utility class instance. pass qgis supplied iface
utils = utilities.Utils(iface)

# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()

# user options table name
#TODO: should be global parameter
userOptionsTable = "availableSoilTableJoins"

#========= validate user input
# returns (message, boolean)
#TODO: validate data
# msg, status = utils.validateUserInput(soil_database, slc_shapefile)
# if not status:
#     # problem with data provided
#     utils.communicateWithUserInQgis("Problem with either: paths or type of data passed in. Stopping.",level="CRITICAL", messageExistanceDuration=15)
#     raise Exception(msg)

#========== load layers
# load soil db table "permittedOperations" into canvas
#TODO: should check in input validation
if soil_database == "":
    # user must supply this!
    utils.communicateWithUserInQgis("Must supply soil datbase path. Stopping.",level="CRITICAL", messageExistanceDuration=15)
    raise Exception("Must supply soil datbase path. Stopping.")
else:
    # user supplied path
    msg, status = utils.loadDbTableAsLayerIntoQgis(soil_database, userOptionsTable)
    if not status:
        # problem loading table
        utils.communicateWithUserInQgis("Problem with either: paths or type of data passed in. Stopping.",level="CRITICAL", messageExistanceDuration=15)
        raise Exception(msg)

# load slc shapefile
if not slc_shapefile =="":
    # user supplied path
    msg, status = utils.loadVectorLayerIntoQgis(slc_shapefile)
    if not status:
        # problem loading table
        utils.communicateWithUserInQgis("Problem with vector layer provided. Stopping.",level="CRITICAL", messageExistanceDuration=15)
        raise Exception(msg)

# create database class instance
# db must exist before sqlite connection can exit
db = database.Db(soil_database, tempSystemDirectoryPath)

# load cmp table
msg, status = utils.loadDbTableAsLayerIntoQgis(soil_database, "cmp")
if not status:
    # problem loading table
    utils.communicateWithUserInQgis("Problem loading cmp soil table. Issue with either: paths or type of data passed in. Stopping.",level="CRITICAL", messageExistanceDuration=15)
    raise Exception(msg)

# load joinedSoilTables or similar named soil joined tables
msg, status = utils.loadDbTableAsLayerIntoQgis(soil_database, db.joinTableName)
if not status:
    # table does not exist. this is okay, perhaps user did not load snf/slf and/or create a joined table before connecting
    pass

#========== clean up
# remove added aafc soil module from python path
sys.path.pop()