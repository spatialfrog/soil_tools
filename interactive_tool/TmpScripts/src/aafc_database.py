"""
handles all interactions with the sqlite db
"""

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import os
import sqlite3


# TODO refactor. executeSql method only one to interact with db via sql

class Db:
    """
    handles all db activities.
    """

    def __init__(self, sqliteDbPath, tmpSystemDirectory):
        # db path
        self.sqliteDbPath = sqliteDbPath

        # db connection
        self.conn = sqlite3.connect(sqliteDbPath)
        self.curs = self.conn.cursor()

        # temp system directory
        self.tmpDirectory = tmpSystemDirectory


    def updateDbTableName(self,tableName):
        """
        perhaps better way?

        sql update name of initial loaded cmp table. when db created, table name
        is set to db file name. set this to the dbf name.
        """

        # get basename of db path minus extension
        tmp = os.path.splitext(os.path.basename(self.sqliteDbPath))[0]
        # convert to lowercase. sqlite tables are all lower.
        baseDbName = tmp.lower()

        # update table name via sql
        sql = "alter table %s rename to %s" % (baseDbName,tableName)
        results = self.executeSql(sql)


    def cleanDbQueryResults(self,data):
        """
        transform data returned from sqlite database.

        return single list of values.
        """

        extractedData = []

        for item in data:
            # extract first item from tuple
            extractedData.append(item[0])

        return extractedData


    def determineFieldDataType(self,data):
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


    def executeSql(self,sqlString):
        """
        calculate sql statement.

        return all rows from query. (list of tuples).
        """

        self.curs.execute(sqlString)

        # return all rows
        return self.curs.fetchall()


    def getFieldNames(self,sqlString):
        """
        return listing of query field names.
        """

        self.curs.execute(sqlString)

        # extract first item from tuple
        fieldNames = list(map(lambda x: x[0], self.curs.description))

        return fieldNames


    # ========== soil queries between tables
    """
    cmp32 is base table for all quieries. must go in order of cmp32 -- snf32 -- slf32.
    soilkey is pk in cmp and fk in other 2 tables.

    ** for a single SLC polygon, we join all soilkeys from cmp table to the other tables.

    if snf, must choose either landuse of A or N; if A absent then assume N. 1:2 relationship possible between cmp soilkey.
    * strip the N/A off cmp soilkey and search snf soilkey with N/A also stripped. if user specified N/A found;
      join on that; else default to the avaiable landuse N/A soilkey.

    if slf, user can only select 1 layer number. 1:many between soilkey.
    slf layer_no appears to be layer number.
    """

    def tmpDbTestQuriesSingleTable(self,tableName="cmp32"):
        """
        test queries against single table.
        """

        # get listing of all tables
        self.curs.execute("select name from sqlite_master where type='table'")
        print self.curs.fetchall()

        # get column names
        sql = "select * from %s limit 1" % (tableName)
        self.curs.execute(sql)

        # clean up
        headers = list(map(lambda x:x[0], self.curs.description))
        print headers

        # get first 10 rows
        sql = "select * from % limit 10" % (tableName)
        self.curs.execute(sql)
        rows = self.curs.fetchall()
        print rows

        # get first 10 distinct sl id's
        sql = "select distinct(sl) from %s" % (tableName)

        results = self.executeSql(sql)
        print "\nDistinct SL id's. Only showing 10 results from several thousand."
        print results[:10]



    def tmpDbTestQuriesTableCmpSnf(self,cmpTableName,snfTableName,soilKey,slcId):
        """
        test queries against join between cmp and snf table via single soilkey.

        return columns hardcoded @ moment.
        """

        sql = """select %s.soilkey as %s_soilkey,%s.slope,%s.soilkey as %s_soilkey,%s.'order',
        %s.g_group3 from %s join %s on %s.soilkey = %s.soilkey where %s.soilkey
        like %s and %s.sl = %s""" % (cmpTableName,cmpTableName,cmpTableName,snfTableName,snfTableName,snfTableName,snfTableName,cmpTableName,snfTableName,cmpTableName,snfTableName,cmpTableName,soilKey,cmpTableName,slcId)

#        sql = """select cmp32.soilkey as cmp32_soilkey,cmp32.slope,snf32.soilkey as snf32_soilkey,snf32.'order',
#        snf32.g_group3 from cmp32 join snf32 on cmp32.soilkey = snf32.soilkey where cmp32.soilkey
#        like "ABBUFgl###N" and cmp32.sl = 242021"""

        self.curs.execute(sql)
        results = self.curs.fetchall()

        # get column headers for pretty print
        headers = list(map(lambda x: x[0], self.curs.description))

        print headers
        print results


    def joinAllCmpRows(self):
        """
        TODO: implement

        link all soilkeys for single SLC id from cmp table to snf table - with user defined snf landuse of either N/A.
        if A not present, default to A.

        each row from cmp will have corresponding row from snf.

        soil key ABABC### provides both N and A option
        """

        pass


    def matchSoilkeyLanduse(self,key,table="snf32",landuse="N"):
        """

        TODO: soil key ABABC### provides both N and A option

        provide cmp soilkey to match landuse on.

        strip soilkey of last character. search snf table for all matches.
        if landuse character present in table soilkey; return soilkey; else
        return avaibale soilkey.
        """

        pass


    def createJoinResultsTable(self,slcId):
        """
        TODO method to create tmp table populated with all joined rows for single slc from cmp table to snf

        create single tmp table to hold row results from single sl cmp join to snf table.

        slcId is int of slc to process.
        """

        pass


    # ========== categorical and numeric calculation methods
    """
    ** these methods must be generic enough to process single sl or the
    entire table of unique sl id's
    """

    def calculateCategoricalField(self):
        """
        TODO: implement
        - only show sub-dominate if dominate % < 60
        - % has no wieght on sub-dominate. take first one.
        - * check if result class = ""; replace with "NULL"

        calculates dominate/sub-dominate results for single string db field

        returns sl ids,rows
        """

        pass


    def calculateNumericField(self):
        """
        TODO implement

        calculates weighted summed average of single numeric db field.

        returns sl ids,rows
        """

        pass

    # ========== categorical/numeric demos

    def demoCalcNumeric(self,sl=254001,tableName="cmp32",column="cfrag1_v"):
        """
        demo output for client. show pretty print output of business logic.

        calculate numeric weighting
        """

        print "\n" + "="*20 + " numeric calculation for sl %s" %(sl)
        sql = """select %s,percent from %s where sl = %s""" %(column,tableName,sl)
        results = self.executeSql(sql)
        print "Rows for %s, percent columns prior to calculation" %(column)
        print results
        print "-"*20
        # - output of calculation
        print "-"*10 +"results"
        sql = """select distinct(sl) as sl, sum(%s * (percent/100.0)) as final from %s where sl = %s group by sl""" %(column,tableName,sl)
        results = self.executeSql(sql)
        print "Calculated weighted sum for %s field. sum(%s row * percentage) for each row within single sl id." %(column,column)
        # don't show sl; only the calculated value
        print results[0][1]


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

