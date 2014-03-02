"""
initial snippets of python to work against qgis python interp.

more for familiarity before pushing to actual qgis app.
"""

import os
import sys
import sqlite3

# cmp db table values
# sl id
slId = [242025,254001,]
# fields to calculate on. mix of numeric/text
fieldsToCalculateOn = ["slope","cfrag1_v","stone"]

# input dbf to be converted
dbfPath = r"/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/Soil/SLC-fordistribution/cmp32.dbf"
# output spatialite db. ogr will add extension.
outSqliteDbPath = "/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/cmp32"
# full path to spatialite db
inFilePath = outSqliteDbPath + ".sqlite"

# remove all layers in qgis
QgsMapLayerRegistry.instance().removeAllMapLayers()

# remove spatialite db
if os.path.exists(inFilePath):
    # remove
    os.remove(inFilePath)
    print "removed existing spatialite db."

# ========== QGIS API
# loading allows user to interact with dataset. provides access to gui.
#
# ==== convert dbf to sqlite db
# load as qgis vector layer, but do not display on canvas
dbfLayer = QgsVectorLayer(dbfPath,"tmpTable","ogr")
# write dbf to sqlite. must be spatialite to work for loading back into qgis
QgsVectorFileWriter.writeAsVectorFormat(dbfLayer,outSqliteDbPath,"CP1250",None,"SQLite",False,None,["SPATIALITE=yes"])

# ==== load sqlite db into qgis
# load db layer
dbLayer = QgsVectorLayer('dbname="/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/cmp32.sqlite" table="cmp32"', 'cmp32_db', 'spatialite')
QgsMapLayerRegistry.instance().addMapLayer(dbLayer)


# ========== Python connection Sqlite db
# qgis only provides low level interface, not easy to pass simple sql.
#
# ==== interaction with sqlite db

# create connection
conn = sqlite3.connect(inFilePath)
curs = conn.cursor()

def executeSql(sqlString):
    """
    calculate sql statement.

    return all rows. list of tuples.
    """

    curs.execute(sqlString)

    # return all rows
    return curs.fetchall()

def getFieldNames(sqlString):
    """
    return listing of field names
    """

    curs.execute(sqlString)

    fieldNames = list(map(lambda x: x[0], curs.description))

    return fieldNames

def cleanUp(dbConnection):
    """
    house cleaning prior to script ending.
    """

    dbConnection.close()

def determineFieldDataType(data):
    """
    determine field data type from user passed list.

    cavet: assumes that list is same data type; comes from sql database.

    return single value of "string" or "numeric"
    """

    # get single item to test
    item = data[0]
    itemDataType = "string"
    try:
        item.isalpha()
    except:
        # not string
        itemDataType = "numeric"

    return itemDataType

def cleanDbQueryResults(data):
    """
    transform data returned from sqlite database.

    return single list of values.
    """

    returnData = []

    for item in data:
        # extract first item from tuple
        returnData.append(item[0])

    return returnData


## =  get general info about table
## get listing of unique of sl id's (slc id's)
#sql = """select distinct(sl) from cmp32"""
#results = executeSql(sql)
#print "\nDistinct SL id's. Only showing 10 results from several thousand."
#print results[:10]
#
## get listing of fields
#sql = """select * from cmp32 limit 1"""
#results = getFieldNames(sql)
#print "\nField names"
    #print results

# ===== xiaoyuans business logic
# numeric: calculate weighted sum of column
# - show orginial table data for row
def demoCalcNumeric(sl=254001,tableName="cmp32",column="cfrag1_v"):
    """
    demo output for client. show pretty print output of business logic.

    calculate numeric weighting
    """

    print "\n" + "="*20 + " numeric calculation for sl %s" %(sl)
    sql = """select %s,percent from %s where sl = %s""" %(column,tableName,sl)
    results = executeSql(sql)
    print "Rows for %s, percent columns prior to calculation" %(column)
    print results
    print "-"*20
    # - output of calculation
    print "-"*10 +"results"
    sql = """select distinct(sl) as sl, sum(%s * (percent/100.0)) as final from %s where sl = %s group by sl""" %(column,tableName,sl)
    results = executeSql(sql)
    print "Calculated weighted sum for %s field. sum(%s row * percentage) for each row within single sl id." %(column,column)
    # don't show sl; only the calculated value
    print results[0][1]

def demoCalcCategorical(sl=254001,tableName="cmp32",column="slope"):
    """
    demo output for client. show pretty print output of business logic.

    calculate categorical dominate/sub-dominate.
    """

    # textual: calculate dominate/sub-dominate
    print "="*20 + " categorical calculation for sl %s" %(sl)
    sql = """select %s,percent from %s where sl = %s""" %(column,tableName,sl)
    results = executeSql(sql)
    print "Rows for %s, percent column prior to calculation" %(column)
    print results
    print "-"*20
    print "-"*10 + "results"
    sql = """select distinct(%s),count(%s) as count, sum(percent) as dominance from %s where sl = %s group by %s order by count(%s) desc""" %(column,column,tableName,sl,column,column)
    results = executeSql(sql)
    print "Calculated dominate/sub-dominate raw results for %s.\nCategory -- Count -- Percentage" %(column)
    print results
    print "-"*20

# show demo output
demoCalcCategorical()
demoCalcCategorical(sl=242025,column="cfrag1")
demoCalcCategorical(sl=242025,column="stone")
demoCalcNumeric()
demoCalcNumeric(sl=376001,column="awhc")

# house keeping
cleanUp(dbConnection=conn)