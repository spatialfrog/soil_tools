"""
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
sys.path.append(r"/Users/drownedfrog/Documents/workspace/git/aafc_qgis_soil_tool/TmpScripts/")

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

# == use existing db
"""
use existing spatialite db or create new db
"""
useExistingDb = False


# ========= set high level variables
# full path to spatialite db
inSoilDbPath = os.path.join(sqliteDbPath, sqliteDbName + ".sqlite")



# ========== work flow
# create utility class instance
utils = utilities.Utils(iface)

# get path to temp directory
tempSystemDirectoryPath = utils.determineSystemTempDirectory()

# class instance of io
io = inout.Io(os.path.join(sqliteDbPath, sqliteDbName), tempSystemDirectoryPath)

# check user preference for using existing db or create new one
if useExistingDb:
    # TODO validate user input
    # TODO: user wants to use existing db
    pass
else:
    # validate user input
    utils.validateUserInput(cmpDbfPath)

    # remove existing db if user provides same name
    utils.deleteFile(os.path.join(sqliteDbPath, sqliteDbName))

    # remove all layers in qgis
    utils.removeAllQgisLayers()

    # create new db
    io.createNewDb(cmpDbfPath)

    # create database class instance
    # db must exist before sqlite connection can exit
    db = database.Db(inSoilDbPath, tempSystemDirectoryPath)

    # change initial loaded table to correct table name
    # created db table has name of db. change this to name of dbf
    # TODO: parameterize name from dbf -- might need to be generic in utilities. io.createDb has similar
    db.updateDbTableName("cmp32")

    # get listing of tables
    results = db.executeSql("select name from sqlite_master where type='table'")
    print results


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