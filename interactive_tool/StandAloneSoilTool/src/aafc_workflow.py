"""
version v1

richard burcher
richardburcher@gmail.com 

main script to orchestate pre qgis gui work flows


script designed to test working with all 3 soil dbf's.

prototyping of business logic to combine all 3 into single db &
creating table linkages.
"""

import os
import sys
import sqlite3

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


# TODO: remove from final implementation. not an issue as qgis put .qgis/python/plugins onto sys path
sys.path.append(r"/Users/drownedfrog/Documents/workspace/git/aafc-grip-tool-dev-dec2013-mar2014/interactive_tool/StandAloneSoilTool/src/")

import aafc_io as inout
import aafc_utilities as utilities
import aafc_database as database
import aafc_gui as gui



# ========= inputs to be set via pyqt4 gui
"""
will be passed via pyqt4 gui
"""
# == input paths to dbf's
# cmp dbf to be converted. * must always be passed if not then quit!
cmpDbfPath = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/Soil/SLC-fordistribution/cmp32.dbf"
# snf dbf. landuse table.
snfDbfPath = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/Soil/SLC-fordistribution/snf32.dbf"
# slf dbf. layer table.
slfDbfPath = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/Soil/SLC-fordistribution/slf32.dbf"

# == output main db name & path
"""
single spatialite db from cmp dbf; this table is primary table.
then add additional dbf's as new tables.
"""
# output spatialite db. ogr will add extension.
sqliteDbName = "soilDb"
sqliteDbPath = "/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/"


# =========== configuration options.
"""
options user can set and then use run to run.
ie. overwrite files, primary key of tables, default name of csv etc
"""
# == use existing db
useExistingDb = False
existingDbPath = "/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/soilDb.sqlite"

# == delete csv's in directory
# TODO: config -- implement user option to delete all csv's in output directory


# == db fields
"""
field names used for linking; primary/foreign key names
"""
# what is field name in cmp table to define slc id
dbSlcIdKey = "sl"

# what field defines soilkey
dbSoilKey = "soilkey"

# what field reflects percent in cmp
dbPercentKey = "percent"

# what field in cmp table is cmp field. integer field listing unique id
dbCmpKey = "cmp"

# what field in snl table is layer_no field.
dbLayerNumberKey = "layer_no"



# == output directory for csv
"""
could be different than where db is placed
"""
outDirectory = "/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/"


# == csv prefix name for file to be created
"""
default will be calculated
csv name will be prefixed by user supplied name. remainder of name derived from column
"""
csvFilePrefix = "calculated"

# == snf landuse preference
"""
either N or A
default if not A is N
"""
userLandusePreference = "A"

# == slf layer number
userLayerNumber = 4


# == slc ids
# sl from cmp to look at
# 974040 -- exact tie
# 972018 -- 3 values
# 615009 -- 4 unique values + A/N options

slcIds = [974040, 972018, 615009, 242025, 376001]


# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(sqliteDbPath, sqliteDbName + ".sqlite")

# name of table for calculating numeric/categorical
calculationTableName = ""
calculationColumnName = ""

# ========== create class instances
# create utility class instance
utils = utilities.Utils(iface)

# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()

# class instance of io
io = inout.Io(inSoilDbPath, tempSystemDirectoryPath)

#========== create or use existing soil db
if useExistingDb:
    # use existing db
        
    # check path provided exists
    status = utils.checkFileExits(existingDbPath)
    if not status:
        # file path incorrect
        utils.communicateWithUserInQgis("DB path supplied is incorrect. Stopping process.",level="CRITICAL")
        sys.exit()
    
else:
    # create new db
    
    # validate user input
    utils.validateUserInput(cmpDbfPath, snfDbfPath, slfDbfPath)
    
    # get mapping of soil names to use for db from dbf file name paths
    tableNamesToDbfPaths = utils.getTableNamesToPathFromDbfPaths(cmpDbfPath, snfDbfPath, slfDbfPath)
    
    # inform user that db creation is about to start
    utils.communicateWithUserInQgis("Creating new db...",level="INFO", messageExistanceDuration=4)    
    
    # remove existing db if user provides same name
    utils.deleteFile(os.path.join(sqliteDbPath, sqliteDbName))

    #=== create db and load with passed dbf paths
    # create new db
    loadStatus = io.createNewDb(tableNamesToDbfPaths)
    if not loadStatus:
        # issue loading layers qith qgis api
        utils.communicateWithUserInQgis("Problem loading/processing user dbf files into spatialdb. Is dbf okay? Stopping processing!", level="CRITICAL", messageExistanceDuration=10)
        sys.exit()
    
    # create database class instance
    # db must exist before sqlite connection can exit
    db = database.Db(inSoilDbPath, tempSystemDirectoryPath)

    # change initial loaded cmp table name from db name to "cmp"
    db.updateDbTableName("cmp")


#========== Working with db

# list of soil tables present in db
soilTablesPresent = db.getSoilTablesListing()

# user determines what tables they want to work with
tableOptionsForProcessing = utils.getTableProcessingOptions(soilTablesPresent)

#TODO: gui -- show user avaiable table options to select

# user selection from gui for table(s) to work with
userTableSelection = 2

# user selection for table to use for column calculation
if userTableSelection == 0:
    # no join. cmp table
    calculationTableName = "cmp"
    
elif userTableSelection == 1:
    # join requested
    # 2 table join -- cmp - snf tables
    db.resultsTableJoiningCmpSnfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, cmpTableName="cmp", snfTableName="snf", landuse=userLandusePreference, writeTestCsv=False, writeTestCsvDirectory=None)
    calculationTableName = db.joinTableName
    
elif userTableSelection == 2:
    # 3 table join -- cmp - snf - slf
    db.resultsTableJoiningCmpSnfSlfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, dbLayerNumberKey=dbLayerNumberKey, cmpTableName="cmp", snfTableName="snf", slfTableName="slf", landuse=userLandusePreference, layerNumber=userLayerNumber)
    calculationTableName = db.joinTableName
    
# get fields present from user option for tables requested to work with
fieldsPresent = db.getTableFieldNames(calculationTableName)

#TODO: gui -- show all fields that can be selected. must quote name as '"name"'

# get user selected field for calculation
calculationColumnName = '"domsand"'

#===== process field
# warn user process may take several minutes
message = "Calculating column %s may take several minutes" % (calculationColumnName)
utils.communicateWithUserInQgis(message,messageExistanceDuration=10)

headers, results = db.calculateField(slcIds, dbSlcKey=dbSlcIdKey, tableName=calculationTableName, columnName=calculationColumnName, dbPercentKey=dbPercentKey)

print headers
print results

io.writeCsvFile(calculationColumnName, headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)


# inform user processing finished
msg = "Finished processing column %s. Find output CSV in directory %s" %(calculationColumnName, outDirectory)
utils.communicateWithUserInQgis(msg, messageExistanceDuration=10)

    
    

print "========= done ========"
# clean up
# utils.cleanUp(db.conn)

#TODO: remove -- when plugin built. no longer required to clean up system path
sys.path.pop()
