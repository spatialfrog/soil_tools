#TODO: add doc string

#==========
# sets up gui in qgis processing framework
##[AAFC Soil Tools]=group
##sqlite_database_name=string soilDb
##sqlite_database_folder=folder
##cmp_dbf_path=file
##snf_dbf_path=file
##slf_dbf_path=file
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
import aafc_io as inout
import aafc_utilities as utilities
import aafc_database as database

# create utility class instance. pass qgis supplied iface
utils = utilities.Utils(iface)

# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(sqlite_database_folder, sqlite_database_name + ".sqlite")
 
# ========== create class instances
# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()
 
# class instance of io
io = inout.Io(inSoilDbPath=inSoilDbPath, tempSystemDirectoryPath=tempSystemDirectoryPath)


#========== create new db
    
#TODO: validate -- check return status and inform user/quite script without killing qgis in process  
# validate user input
utils.validateUserInput(cmp_dbf_path, snf_dbf_path, slf_dbf_path)
  
# get mapping of soil names to use for db from dbf file name paths
tableNamesToDbfPaths = utils.getTableNamesToPathFromDbfPaths(cmp_dbf_path, snf_dbf_path, slf_dbf_path)
  
# inform user that db creation is about to start
utils.communicateWithUserInQgis("Creating new db...",level="INFO", messageExistanceDuration=4)    
  
# remove existing db if user provides same name
utils.deleteFile(os.path.join(sqlite_database_folder, sqlite_database_name))

#========== create db and load with passed dbf paths
# create new db
loadStatus = io.createNewDb(tableNamesToDbfPaths)
if not loadStatus:
    # issue loading layers qith qgis api
    utils.communicateWithUserInQgis("Problem loading/processing user dbf files into spatialdb. Is dbf okay? Stopping processing!", level="CRITICAL", messageExistanceDuration=10)
    print "----- issue"
    #TODO: how to exit gracefully without killing qgis
    #sys.exit()
  
# create database class instance
# db must exist before sqlite connection can exit
db = database.Db(inSoilDbPath, tempSystemDirectoryPath)

# change initial loaded cmp table name from db name to "cmp"
db.updateDbTableName("cmp")

# report db creation success
msg = "Db successfully created. Find in directory %s" %(sqlite_database_folder)
utils.communicateWithUserInQgis(msg, messageExistanceDuration=10)


# remove added aafc soil module from python path
sys.path.pop()
