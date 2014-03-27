"""
purpose:
create a join table linking cmp + snf or cmp + snf + slf

notes:
-join is dynamic. based on user tables + join criteria
-join based on linking cmp table slc id + each cmp id row for that slc (this makes unique cmp row) by soilkey to snf and then slf if requested. the
result is a single row per slc id + cmp in the new join table
-for each run of this script, the "joinedResults" join table is dropped and recreated
-user must select shapefile column that defines the slc ids. thses are used for processing
if no polygons selected than all polygons processed
-join driven by user selected "permittedOperations" gui selection. depending on soil tables in db, user
can either select cmp, cmp-snf or cmp-snf-slf
-tables joined by soilkey or soilmap column
-for snf table join, the user land user preference of A/N can be selected. default selection is N if user choice can not be accomidated
-for slf table, layer number used to select row. if user selected layer number not found, then that join row will be dropped

input:
-slc shapefile field defining the slc ids
-join option provided by "availableSoilTableJoins"

output:
-added table to soil db named "joinedResults"
-join table will be added to qgis toc for selection in next script
-table is used by next script to calculate soil attributes

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
##available_soil_table_joins=table
##soil_tables_to_join=field available_soil_table_joins
##slc_shapefile=vector
##slc_shapefile_polygon_id_column=field slc_shapefile
##user_preference_snf_table_land_use=string A
##user_preference_slf_table_layer_number=number 4
##option_soil_tables_soil_key_column=string soilkey
##option_soil_cmp_table_slc_id_column=string sl
##option_soil_cmp_table_cmp_column=string cmp
##option_soil_cmp_table_percent_column=string percent
##option_soil_slf_table_layer_number_column=string layer_no
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

# get db path from available soil table joins layer in qgis
inSoilDbPath = utils.getQgisTableLayerFilePathInfo(available_soil_table_joins)
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

#TODO: check if vector layer slc ids found in cmp table

#========== join soil tables together
#TODO: should extract column number inplace of using text
if soil_tables_to_join == "cmp-snf":
    # join requested
    # 2 table join -- cmp - snf tables
    db.resultsTableJoiningCmpSnfBySoilkey(slcIds, dbSlcKey=option_soil_cmp_table_slc_id_column, dbCmpKey=option_soil_cmp_table_cmp_column, dbSoilKey=option_soil_tables_soil_key_column, cmpTableName="cmp", snfTableName="snf", landuse=user_preference_snf_table_land_use, writeTestCsv=False, writeTestCsvDirectory=None)
    calculationTableName = db.joinTableName
      
elif soil_tables_to_join == "cmp-snf-slf":
    #TODO: remove this
    outTestTxt = "/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test"
    # 3 table join -- cmp - snf - slf
    db.resultsTableJoiningCmpSnfSlfBySoilkey(slcIds, dbSlcKey=option_soil_cmp_table_slc_id_column, dbCmpKey=option_soil_cmp_table_cmp_column, dbSoilKey=option_soil_tables_soil_key_column, dbLayerNumberKey=option_soil_slf_table_layer_number_column, cmpTableName="cmp", snfTableName="snf", slfTableName="slf", landuse=user_preference_snf_table_land_use, layerNumber=user_preference_slf_table_layer_number, writeTestCsv=True, writeTestCsvDirectory=outTestTxt)
    calculationTableName = db.joinTableName  


#========== create indexes on all columns in join table
# speed up field calculations
db.createDbIndexesOnJoinedTable()

#========== add new join table to qgis
# remove existing join table if present
utils.removeLayerFromQgis(db.joinTableName)
# add created join table to qgis toc
utils.loadDbTableAsLayerIntoQgis(inSoilDbPath, db.joinTableName)

# inform user processing finished
msg = "Finished creating soil table joins for tables %s" %(soil_tables_to_join)
utils.communicateWithUserInQgis(msg, messageExistanceDuration=10)

#========== clean up
# remove added aafc soil module from python path
sys.path.pop()