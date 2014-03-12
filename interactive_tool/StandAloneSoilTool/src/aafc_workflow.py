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
landusePreference = "A"

# == slc ids
# sl from cmp to look at
# 974040 -- exact tie
# 972018 -- 3 values
# 615009 -- 4 unique values + A/N options

slcIds = [974040, 972018, 615009, 242025, 376001]


# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(sqliteDbPath, sqliteDbName + ".sqlite")



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
    
    # remove all layers in qgis
    utils.removeAllQgisLayers()
    
    #TODO: get listing of tables for use. searching for cmp/slf/snf tables
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

    # remove all layers in qgis
    utils.removeAllQgisLayers()

    #=== create db and load with passed dbf paths
    # create new db
    io.createNewDb(tableNamesToDbfPaths)
    
    # create database class instance
    # db must exist before sqlite connection can exit
    db = database.Db(inSoilDbPath, tempSystemDirectoryPath)

    # change initial loaded cmp table name from db name to "cmp"
    db.updateDbTableName("cmp")


#========== Working with db

# list of soil tables present in db
soilTablesPresent = db.getSoilTablesListing()

# user determines if join occuring based on tables selected
tableOptionsForProcessing = utils.getTableProcessingOptions(soilTablesPresent.keys())

#TODO: gui -- show user avaiable table options to select


# is table join occuring
if tableOptionsForProcessing == 1:
    # join requested
    # 2 table join -- cmp - snf tables
    db.resultsTableJoiningCmpSnfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, cmpTableName="cmp", snfTableName="snf", landuse=landusePreference, writeTestCsv=False, writeTestCsvDirectory=None)
elif tableOptionsForProcessing == 2:
    # 3 table join -- cmp - snf - slf
    db.resultsTableJoiningCmpSnfSlfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, dbLayerNumberKey=dbLayerNumberKey, cmpTableName="cmp", snfTableName="snf", slfTableName="slf", landuse=landusePreference, layerNumber=dbLayerNumberKey)
    

#======== calculations

#===== process single column categorical
# write all sl's for single column to csv
# warn user process may take several minutes
message = "Calculating column %s may take several minutes" % ("slope")
utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
# get all distinct id's from cmp table
ids = db.executeSql("select distinct(sl) from cmp32")
# convert sl ids list of tuples to simple list
ids_cleaned = utils.convertDbResults2SimpleList(ids)
headers, results = db.calculateField(ids_cleaned[:5], dbSlcKey=dbSlcIdKey, tableName="cmp32", columnName='"slope"', dbPercentKey=dbPercentKey)
io.writeCsvFile("slope", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)


#===== process single column numeric
# write all sl's for single column to csv
# warn user process may take several minutes
message = "Calculating column %s may take several minutes" % ("awhc_v")
utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
# get all distinct id's from cmp table
ids = db.executeSql("select distinct(sl) from cmp32")
# convert sl ids list of tuples to simple list
ids_cleaned = utils.convertDbResults2SimpleList(ids)
headers, results = db.calculateField(ids_cleaned[:5], dbSlcKey=dbSlcIdKey, tableName="cmp32", columnName='"awhc_v"', dbPercentKey=dbPercentKey)
io.writeCsvFile("awhc_v", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)


#===== 2 table join 
# cmp to snf tables
db.resultsTableJoiningCmpSnfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, cmpTableName="cmp32", snfTableName="snf32", landuse=landusePreference, writeTestCsv=False, writeTestCsvDirectory=None)

# categorical calc on joined column g_group3; snf column
message = "Calculating column %s may take several minutes" % ("g_group3")
utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
# get all distinct id's from cmp table
ids = db.executeSql("select distinct(sl) from results_joinedCmpSnf")
# convert sl ids list of tuples to simple list
ids_cleaned = utils.convertDbResults2SimpleList(ids)
headers, results = db.calculateField(ids_cleaned, dbSlcKey=dbSlcIdKey, tableName="results_joinedCmpSnf", columnName='"g_group3:1"', dbPercentKey=dbPercentKey)
io.writeCsvFile("'g_group3:1'", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)


#====== 3 table join 
db.resultsTableJoiningCmpSnfSlfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, dbLayerNumberKey=dbLayerNumberKey, cmpTableName="cmp32", snfTableName="snf32", slfTableName="slf32", landuse=landusePreference, layerNumber=4)
# categorical calc on joined column domsand; slf column
message = "Calculating column %s may take several minutes" % ("domsand")
utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
# get all distinct id's from cmp table
ids = db.executeSql("select distinct(sl) from results_joinedCmpSnfSlf")
# convert sl ids list of tuples to simple list
ids_cleaned = utils.convertDbResults2SimpleList(ids)
headers, results = db.calculateField(ids_cleaned, dbSlcKey=dbSlcIdKey, tableName="results_joinedCmpSnfSlf", columnName='"domsand"', dbPercentKey=dbPercentKey)
io.writeCsvFile("'domsand'", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)
    
    
    

print "========= done ========"
# clean up
# utils.cleanUp(db.conn)
sys.path.pop()
