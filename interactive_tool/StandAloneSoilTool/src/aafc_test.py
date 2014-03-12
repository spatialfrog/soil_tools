"""
test suite
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
sys.path.append(r"/Users/drownedfrog/Documents/workspace/git/aafc-grip-tool-dev-dec2013-mar2014/interactive_tool/StandAloneSoilTool/src")

import aafc_io as inout
import aafc_utilities as utilities
import aafc_database as database


# root directories
dbfDirectory = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/Soil/SLC-fordistribution/"
outDirectory = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/"


# == input paths to dbf's
# cmp dbf to be converted. * must always be passed if not then quit!
cmpDbfPath = os.path.join(dbfDirectory,"cmp32.dbf")
# snf dbf. landuse table.
snfDbfPath = os.path.join(dbfDirectory,"snf32.dbf")
# slf dbf. layer table.
slfDbfPath = os.path.join(dbfDirectory,"slf32.dbf")


# == output main db name & path
# output spatialite db. ogr will add extension.
sqliteDbName = "soilDb_testSuite"

# =========== configuration options.

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


# == prefix name for file to be created
filePrefix = "test"

# == snf landuse preference
"""
either N or A
default if not A is N
"""
landusePreference = "A"

# == slf layer number
# with test slcIds, this ensure several rows are dropped
layerNumberToUse = 4


# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(outDirectory, sqliteDbName + ".sqlite")


# ==================================== work flow
# create utility class instance
utils = utilities.Utils(iface)

#== message user via qgis that testing is taking place
utils.communicateWithUserInQgis("Running test suite. Please be patient, may take several minutes.", level="INFO", messageExistanceDuration=4)

# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()

# class instance of io
io = inout.Io(inSoilDbPath, tempSystemDirectoryPath)

# validate user input
utils.validateUserInput(cmpDbfPath, snfDbfPath, slfDbfPath)

# get mapping of soil names to use for db from dbf file name paths
tableNamesToDbfPaths = utils.getTableNamesToPathFromDbfPaths(cmpDbfPath, snfDbfPath, slfDbfPath)

# remove existing db if user provides same name
utils.deleteFile(os.path.join(outDirectory, sqliteDbName))

# remove all layers in qgis
utils.removeAllQgisLayers()

#=== create db and load with passed dbf paths
# create new db
io.createNewDb(tableNamesToDbfPaths)

# create database class instance
# db must exist before sqlite connection can exit
db = database.Db(inSoilDbPath, tempSystemDirectoryPath)

# change initial loaded table to correct table name
# created db table has name of db. change this to name of dbf
# TODO: parameterize name from dbf -- might need to be generic in utilities. io.createDb has similar
db.updateDbTableName("cmp")


#======== calculations
#TODO: 1 critical --- parameterize all method arguments below

# sl from cmp to look at
# 974040 -- exact tie
# 972018 -- 3 values
# 615009 -- 4 unique values + A/N options

slcIds = [974040, 972018, 615009, 242025, 376001]

#===== test numeric/categorical calculations 
"""
test on selected slc ids
"""


def proveSingleColumnCalculation(slcs, dbSlcKey, dbPercentKey, tableName, columnName, filePrefix, outDirectory):
    """
    input:
    list of slc's to process
    
    calculate numeric weighting or categorical dominate based on column data type
    
    output:
    write single text file
    """
    
    # open file
    with open(os.path.join(outDirectory,filePrefix + "_" + columnName +".txt"),"w") as file_open:
        for id in slcs:
            # get rows for calculation
            sql = "select %s, %s, %s from %s where %s = %s" %(dbSlcKey, columnName, dbPercentKey, tableName, dbSlcKey, id)
            headers, results = db.executeSql(sql, fieldNames=True)
            
            # write intro to file
            msg = "column: %s\nSLC id %s\n" %(columnName, id)
            file_open.write(msg)
            
            # write headers
            writeHeaders = "%s, %s, %s" %(headers[0], headers[1], headers[2])
            file_open.write(writeHeaders)
            file_open.write("\n")
            
            # print each row of data per sl
            for e in results:
                file_open.writelines(str(e))
                file_open.write("\n")
            
            msg = "----- Calculation -----\n"
            file_open.write(msg)
            
            # calculate final value 
            headers, results = db.calculateField([id], dbSlcKey, tableName, columnName, dbPercentKey)
            
            # write result
            file_open.writelines(str(results[0]))
            file_open.write("\n\n")


#============= single column calculation verification
# categorical
proveSingleColumnCalculation(slcIds, dbSlcKey=dbSlcIdKey, dbPercentKey=dbPercentKey, tableName="cmp32", columnName='"slope"', filePrefix=filePrefix, outDirectory=outDirectory)

# numeric
proveSingleColumnCalculation(slcIds, dbSlcKey=dbSlcIdKey, dbPercentKey=dbPercentKey, tableName="cmp32", columnName='"awhc_v"', filePrefix=filePrefix, outDirectory=outDirectory)



#============== table joins
#TODO: testing -- write final join results table to csv

#===== 2 table join
#== cmp to snf table via soilkey

# create join table
db.resultsTableJoiningCmpSnfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, cmpTableName="cmp32", snfTableName="snf32", landuse=landusePreference, writeTestCsv=True, writeTestCsvDirectory=outDirectory)

# categorical calc on joined table. snf column tested.
proveSingleColumnCalculation(slcIds, dbSlcKey=dbSlcIdKey, dbPercentKey=dbPercentKey, tableName=db.joinTableName, columnName='"g_group3:1"', filePrefix=filePrefix, outDirectory=outDirectory)

# numerical calc on joined table. snf column tested.
proveSingleColumnCalculation(slcIds, dbSlcKey=dbSlcIdKey, dbPercentKey=dbPercentKey, tableName=db.joinTableName, columnName='"rootrestri"', filePrefix=filePrefix, outDirectory=outDirectory)


#====== 3 table join
#== cmp - snf - slf via soilkey and layer number in slf
db.resultsTableJoiningCmpSnfSlfBySoilkey(slcIds, dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, dbLayerNumberKey=dbLayerNumberKey, cmpTableName="cmp32", snfTableName="snf32", slfTableName="slf32", landuse=landusePreference, layerNumber=layerNumberToUse, writeTestCsv=True, writeTestCsvDirectory=outDirectory)

# categorical calc on joined table. snf column tested.
proveSingleColumnCalculation(slcIds, dbSlcKey=dbSlcIdKey, dbPercentKey=dbPercentKey, tableName=db.joinTableName, columnName='"domsand"', filePrefix=filePrefix, outDirectory=outDirectory)

# numerical calc on joined table. snf column tested.
proveSingleColumnCalculation(slcIds, dbSlcKey=dbSlcIdKey, dbPercentKey=dbPercentKey, tableName=db.joinTableName, columnName='"bd"', filePrefix=filePrefix, outDirectory=outDirectory)


#======= testing misc functions
#= listing of tables
results = db.getSoilTablesListing()
print(results)

#= get fieldnames from joined table
results = db.getTableFieldNames(db.joinTableName)
print(results)

#= validate user input
# all paths correct + cmp table supplied
msg, status = utils.validateUserInput(cmpDbfPath,snfDbfPath)
print msg,status

# path incorrect
msg, status = utils.validateUserInput(cmpDbfPath,"/Users/me")
print msg, status

# cmp table absent
msg, status = utils.validateUserInput(snfDbfPath,slfDbfPath)
print msg, status

#= mapping of dbf names to paths. keys = table names to create
results = utils.getTableNamesToPathFromDbfPaths(cmpDbfPath, snfDbfPath, slfDbfPath)
print results

#======= CSV writer
#= categorical output "-" removed
# slc 242025 contains "-" for g_group3:1 on cmp - snf table join


#= inappropiate file name characters removed
# any duplicate column from joins will be 'columnName3/number' ie calculated_'g_group3/1'.csv
# cmp-snf table join for g_group3:1 column


#= do not print data rows with None
# slc 376001 for 3 table join, column domsand is None if layer number = 4


#==== clean up
msg = "Finished running test suite. Find results in %s" %(outDirectory)
utils.communicateWithUserInQgis(msg, level="INFO", messageExistanceDuration=10)
sys.path.pop()
