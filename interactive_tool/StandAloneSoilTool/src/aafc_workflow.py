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


# slc ids to process
slcIds = [974040, 972018, 615009, 242025, 376001, 242021]
# name of table for calculating numeric/categorical
calculationTableName = ""
calculationColumnName = ""

# config file name
configFileName = "config.txt"

# script launch directory
scriptDirectory = os.path.dirname((os.path.realpath(sys.argv[0])))

#TODO: error checking --- ensure it;'s robust and places where failure could occur delat with

# create utility class instance
utils = utilities.Utils(iface)

# default configuration settings
def configDefaultFileSettings():
    """
    purpose:
    provide default config file settings if config missing
    
    returns:
    dict of key value pairs to be written to disk
    """
    
    configSettings = {}
    
    # dbf paths
    configSettings["cmpDbfPath"] = "user supplied"
    configSettings["snfDbfPath"] = "user supplied"
    configSettings["slfDbfPath"] = "user supplied"
    
    # db 
    configSettings["sqliteDbName"] = "soilDb"
    configSettings["sqliteDbPath"] = "user supplied"
    
    configSettings["useExistingDb"] = False
    configSettings["existingDbPath"] = "user supplied"
    
    # clean up
    configSettings["removeCurrentCsvs"] = True
    
    #= db key column fields. used for joining and supporting queries 
    # slc id key in cmp table
    configSettings["dbSlcIdKey"] = "sl"
    # soil key or soil map key used to link tables
    configSettings["dbSoilKey"] = "soilkey"
    # cmp percent column
    configSettings["dbPercentKey"] = "percent"
    # cmp column representing the individual component fields within an slc id
    configSettings["dbCmpKey"] = "cmp"
    # slf column representing layer number
    configSettings["dbLayerNumberKey"] = "layer_no"
    
    #= csv
    # write directory
    configSettings["outDirectory"] = "user supplied"
    # prefix for files. user determined
    configSettings["csvFilePrefix"] = "calculated"
    
    #= soil preferences
    # snf land use type. either A/N; agriculture or non-argiculture
    configSettings["userLandusePreference"] = "A"
    # slf layer number
    configSettings["userLayerNumber"] = 4
    
    
    return configSettings

print "wow"
# check if config file exists. will be found in plugin script directory



#TODO: config file --- check if file exists, if not then write initial config using stored default key/values
#TODO: config file --- write dict to store all keys with default values where applicable

# ========= inputs to be set via pyqt4 gui
configFileStatus = utils.checkFileExits(os.path.join(scriptDirectory,configFileName))

# check if configuration file present in root of python script
if not configFileStatus:
    # missing file
    # write new config file
    defaultConfig = configDefaultFileSettings()
    inout.Io.writeConfigFile(scriptDirectory, defaultConfig)

# read configuration file found
configFileParameters = inout.Io.readConfigFile(scriptDirectory, configFileName)

#TODO: config file --- critical -- check config file for correct values and if missing. must stop if issue and inform user

# TODO: config file --- implement user option to delete all csv's in output directory


# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(sqliteDbPath=sqliteDbPath, sqliteDbName=sqliteDbName + ".sqlite")

# ========== create class instances
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
io.writeCsvFile(calculationColumnName, headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)


# inform user processing finished
msg = "Finished processing column %s. Find output CSV in directory %s" %(calculationColumnName, outDirectory)
utils.communicateWithUserInQgis(msg, messageExistanceDuration=10)

    
    

print "========= done ========"
# clean up
# utils.cleanUp(db.conn)

#TODO: remove -- when plugin built. no longer required to clean up system path
sys.path.pop()
