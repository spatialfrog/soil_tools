"""
purpose:
process given table and calculate each column

notes:
user must select shapefile column that defines the slc ids. these are used for processing
if no polygons selected than all polygons processed

input:
slc shapefile field defining the slc ids
table for processing

output:
-csv for each column
-does not load into qgis

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
##soil_table=table
##slc_shapefile=vector
##slc_shapefile_polygon_id_column=field slc_shapefile
##option_soil_cmp_table_slc_id_column=string sl
##option_soil_cmp_table_percent_column=string percent
##option_csv_output_directory=folder
##option_csv_file_prefix=string calculation
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

# ========== create class instances
# create utility class instance. pass qgis supplied iface
utils = utilities.Utils(iface)

# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()
 
# io instance
io = inout.Io(tempSystemDirectoryPath=tempSystemDirectoryPath)

# get db path from cmp layer in qgis
inSoilDbPath = utils.getQgisTableLayerFilePathInfo(soil_table)
# db instance
db = database.Db(inSoilDbPath, tempSystemDirectoryPath)

# db performance tuning
db.sqliteLoadingPerformanceTuning(enable=True)

#========== get spatial selection of polygon slc units to process
# if no sub-selection, assume all polygons to be processed
msg,slcIds,status = utils.getVectorLayerFieldValues(slc_shapefile, slc_shapefile_polygon_id_column)
if not status:
    # problem with getting values from vector layer for slc ids
    utils.communicateWithUserInQgis("No values for field in given vector layer for slc ids. Stopping.",level="CRITICAL", messageExistanceDuration=15)
    raise Exception(msg)

# warn user process may take several minutes
message = "Calculating all columns for table %s may take several minutes" % (soil_table)
utils.communicateWithUserInQgis(message,messageExistanceDuration=10)
 
#===== process each column
#TODO: should be able to exclude certain columns ie slc, percent, soilkey

# convert full connection path of user selected table in qgis toc to actual table name
tableName = utils.getQgisTableLayerFilePathInfo(soil_table, pathKey="table")

# get listing of fields in table
columnsToProcess = db.getTableFieldNames(tableName)

for column in columnsToProcess:
    # process each column
    # column field must be qouted as '"field_to_calculate"'
    calculationColumnName = '"%s"' %(column)
    
    # calculate column
    headers, results = db.calculateField(slcIds, dbSlcKey=option_soil_cmp_table_slc_id_column, tableName=tableName, columnName=calculationColumnName, dbPercentKey=option_soil_cmp_table_percent_column)
    outCsvFilePath = io.writeCsvFile(calculationColumnName, headers, results, option_csv_output_directory, csvFilePrefixName=option_csv_file_prefix)

# inform user processing finished
msg = "Finished processing all columns for table %s. Find output CSV in directory %s" %(soil_table, option_csv_output_directory)
utils.communicateWithUserInQgis(msg, messageExistanceDuration=10)

#========== clean up
# remove added aafc soil module from python path
sys.path.pop()