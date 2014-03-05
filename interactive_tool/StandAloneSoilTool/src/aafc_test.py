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
sys.path.append(r"/Users/drownedfrog/Documents/workspace/git/aafc-grip-tool-dev-dec2013-mar2014/interactive_tool/StandAloneSoilTool/src/")

import aafc_io as inout
import aafc_utilities as utilities
import aafc_database as database
import aafc_gui as gui


# root directories
dbfDirectory = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/Soil/SLC-fordistribution"
outDirectory = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test"


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
sqliteDbPath = os.path.join(outDirectory, sqliteDbName)


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


# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(sqliteDbPath, sqliteDbName + ".sqlite")


# ==================================== work flow
# create utility class instance
utils = utilities.Utils(iface)

# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()

# class instance of io
io = inout.Io(inSoilDbPath, tempSystemDirectoryPath)

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


#======== calculations
#TODO: 1 critical --- parameterize all method arguments below

# sl from cmp to look at
# 974040 -- exact tie
# 972018 -- 3 values
# 615009 -- 4 unique values + A/N options


#===== test numeric/categorical calculations 
"""
test on selected slc ids
"""


def calcNumeric(slcs, dbSlcKey, dbPercentKey, tableName="cmp32", columnName="cfrag1_v", filePrefix, outDirectory):
    """
    input:
    list of slc's to process
    
    calculate numeric weighting
    
    output:
    write single csv file
    """
    
    # open file
    with open(os.path.join(outDirectory,filePrefix + "_" + columnName +".txt"),"w") as file_open:
        for id in slcs:
            # get rows for calculation
            sql = "select %s, %s from %s where %s = %s" %(dbSlcKey, dbPercentKey, tableName, dbSlcKey, id)
            headers, results = db.executeSql(sql, fieldNames=True)
            
            # write intro to file
            msg = "SLC id %s rows for column %s\n" %(id, columnName)
            file_open.write(msg)
            
            # write headers
            file_open.write(headers)
            
            # calculate final value 
            headers, results = db.calculateField([id], dbSlcKey=dbSlcIdKey, tableName=tableName, column=columnName, dbPercentKey=dbPercentKey)
            
            # write result
            file_open.write(results)
            file_open.write("\n\n")
        

def demoCalcCategorical(self,sl=254001,tableName="cmp32",column="slope"):
    """
    demo output for client. show pretty print output of business logic.

    calculate categorical dominate/sub-dominate.
    """

    # textual: calculate dominate/sub-dominate
    print "="*20 + " categorical calculation for sl %s" %(sl)
    sql = """select %s,percent from %s where sl = %s""" %(column,tableName,sl)
    results = self.executeSql(sql)
    print "Rows for %s, percent column prior to calculation" %(column)
    print results
    print "-"*20
    print "-"*10 + "results"
    sql = """select distinct(%s),count(%s) as count, sum(percent) as dominance from %s where sl = %s group by %s order by count(%s) desc""" %(column,column,tableName,sl,column,column)
    results = self.executeSql(sql)
    print "Calculated dominate/sub-dominate raw results for %s.\nCategory -- Count -- Percentage" %(column)
    print results
    print "-"*20


def demoCategoricalColumnToCsv(self, sl=254001, tableName="cmp32", column="slope"):
    """
    demo to return categorical calculation.
    
    returns headers and row data to write to csv.
    """
    
    # query
    sql = """select distinct(%s),count(%s) as count, sum(percent) as dominance from %s where sl = %s group by %s order by count(%s) desc""" %(column,column,tableName,sl,column,column)
    headers, results = self.executeSql(sql,fieldNames=True)
    
    # return headers + results
    return headers, results
    


def demoSimpleJoinBetweenCmpSnfTables(self, cmpTableName="cmp32", snfTableName="snf32", soilKey="ABBUFgl###N", slcId=242021):
    """
    simple join between cmp and snf table via single soilkey.

    return columns hardcoded @ moment.
    """

    sql = """select %s.soilkey as %s_soilkey,%s.slope,%s.soilkey as %s_soilkey,%s.'order',
    %s.g_group3 from %s join %s on %s.soilkey = %s.soilkey where %s.soilkey
    like %s and %s.sl = %s""" % (cmpTableName,cmpTableName,cmpTableName,snfTableName,snfTableName,snfTableName,snfTableName,cmpTableName,snfTableName,cmpTableName,snfTableName,cmpTableName,soilKey,cmpTableName,slcId)

#        sql = """select cmp32.soilkey as cmp32_soilkey,cmp32.slope,snf32.soilkey as snf32_soilkey,snf32.'order',
#        snf32.g_group3 from cmp32 join snf32 on cmp32.soilkey = snf32.soilkey where cmp32.soilkey
#        like "ABBUFgl###N" and cmp32.sl = 242021"""
    
    print sql
    
    headers, results = self.executeSql(sql,fieldNames=True)

    print headers
    print results






#== categorical
# slope column
headers, results = db.calculateField([615009], dbSlcKey=dbSlcIdKey, tableName="cmp32", column="slope", dbPercentKey=dbPercentKey)
io.writeCsvFile("slope", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)


#== numeric
# awhc_v column
headers, results = db.calculateField([615009], dbSlcKey=dbSlcIdKey, tableName="cmp32", column="awhc_v", dbPercentKey=dbPercentKey)
io.writeCsvFile("awhc_v", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)


# #===== join cmp to snf tables
# db.resultsTableJoiningCmpSnfBySoilkey([242025,376001,615009], dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, cmpTableName="cmp32", snfTableName="snf32", landuse=landusePreference)
# 
# # categorical calc on joined column g_group3; snf column
# message = "Calculating column %s may take several minutes" % ("g_group3")
# utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
# # get all distinct id's from cmp table
# ids = db.executeSql("select distinct(sl) from results_joinedCmpSnf")
# # convert sl ids list of tuples to simple list
# ids_cleaned = utils.convertDbResults2SimpleList(ids)
# headers, results = db.calculateField(ids_cleaned[:5], dbSlcKey=dbSlcIdKey, tableName="results_joinedCmpSnf", column="g_group3", dbPercentKey=dbPercentKey)
# io.writeCsvFile("'g_group3:1'", headers, results, outDirectory, csvFilePrefixName=csvFilePrefix)
# 
# 
# #====== join all 3 tables together
# db.resultsTableJoiningCmpSnfSlfBySoilkey([242025,376001,615009], dbSlcKey=dbSlcIdKey, dbCmpKey=dbCmpKey, dbSoilKey=dbSoilKey, dbLayerNumberKey=dbLayerNumberKey, cmpTableName="cmp32", snfTableName="snf32", slfTableName="slf32", landuse=landusePreference, layerNumber=1)
