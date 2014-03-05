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


# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(sqliteDbPath, sqliteDbName + ".sqlite")



# ========== work flow
# create utility class instance
utils = utilities.Utils(iface)

# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()

# class instance of io
io = inout.Io(inSoilDbPath, tempSystemDirectoryPath)

# check user preference for using existing db or create new one
if useExistingDb:
    # TODO validate user input
    # TODO: user wants to use existing db
    pass
else:
    # validate user input
    utils.validateUserInput(cmpDbfPath)

    # inform user that db creation is about to start
    utils.communicateWithUserInQgis("Creating new db...",level="INFO", messageExistanceDuration=4)    
    
    # remove existing db if user provides same name
    utils.deleteFile(os.path.join(sqliteDbPath, sqliteDbName))

    # remove all layers in qgis
    utils.removeAllQgisLayers()

    #=== create db and load with passed dbf paths
    # create new db
    io.createNewDb(cmpDbfPath,snfDbfPath,slfDbfPath)
    
    # create database class instance
    # db must exist before sqlite connection can exit
    db = database.Db(inSoilDbPath, tempSystemDirectoryPath)

    # change initial loaded table to correct table name
    # created db table has name of db. change this to name of dbf
    # TODO: parameterize name from dbf -- might need to be generic in utilities. io.createDb has similar
    db.updateDbTableName("cmp32")

    # get listing of tables
    results = db.executeSql("select name from sqlite_master where type='table'")
    #print results
    
    #===== demo to stdout
    db.demoCalcCategorical()
    db.demoCalcNumeric()
    
    
    #======== calculations
    #TODO: 1 critical --- parameterize all method arguments below
    
#     #===== process single column categorical
#     # write all sl's for single column to csv
#     # warn user process may take several minutes
#     message = "Calculating column %s may take several minutes" % ("slope")
#     utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
#     # get all distinct id's from cmp table
#     ids = db.executeSql("select distinct(sl) from cmp32")
#     # convert sl ids list of tuples to simple list
#     ids_cleaned = utils.convertDbResults2SimpleList(ids)
#     headers, results = db.calculateField(ids_cleaned[:5], dbSlcKey=dbSlcIdKey, tableName="cmp32", column="slope", dbPercentKey=dbPercentKey)
#     io.writeCsvFile("slope", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)
# 
# 
#     #===== process single column numeric
#     # write all sl's for single column to csv
#     # warn user process may take several minutes
#     message = "Calculating column %s may take several minutes" % ("awhc_v")
#     utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
#     # get all distinct id's from cmp table
#     ids = db.executeSql("select distinct(sl) from cmp32")
#     # convert sl ids list of tuples to simple list
#     ids_cleaned = utils.convertDbResults2SimpleList(ids)
#     headers, results = db.calculateField(ids_cleaned[:5], dbSlcKey=dbSlcIdKey, tableName="cmp32", column="awhc_v", dbPercentKey=dbPercentKey)
#     io.writeCsvFile("awhc_v", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)
    
    
    #===== join cmp to snf tables
#     db.resultsTableJoiningCmpSnfBySoilkey([242025,376001,615009], dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, cmpTableName="cmp32", snfTableName="snf32", landuse=landusePreference)
#     
#     # categorical calc on joined column g_group3; snf column
#     message = "Calculating column %s may take several minutes" % ("g_group3")
#     utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
#     # get all distinct id's from cmp table
#     ids = db.executeSql("select distinct(sl) from results_joinedCmpSnf")
#     # convert sl ids list of tuples to simple list
#     ids_cleaned = utils.convertDbResults2SimpleList(ids)
#     headers, results = db.calculateField(ids_cleaned[:5], dbSlcKey=dbSlcIdKey, tableName="results_joinedCmpSnf", column="g_group3", dbPercentKey=dbPercentKey)
#     io.writeCsvFile("'g_group3:1'", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)
    
    
    #====== join all 3 tables together
    db.resultsTableJoiningCmpSnfSlfBySoilkey([242025,376001,615009], dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, dbLayerNumberKey=dbLayerNumberKey, cmpTableName="cmp32", snfTableName="snf32", slfTableName="slf32", landuse=landusePreference, layerNumber=1)
    
    
    
    

print "========= done ========"
# clean up
# utils.cleanUp(db.conn)

# remove scripts dir from sys path
sys.path.pop()

## ========= testing
#if __name__ == "main":
#    # run following
#
#    # show demo output
#    demoCalcCategorical()
#    demoCalcCategorical(sl=242025,column="cfrag1")
#    demoCalcCategorical(sl=242025,column="stone")
#    demoCalcNumeric()
#    demoCalcNumeric(sl=376001,column="awhc")
#
#    # house keeping
#    cleanUp(dbConnection=conn)