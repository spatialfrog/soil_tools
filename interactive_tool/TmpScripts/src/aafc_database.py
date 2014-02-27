"""
handles all interactions with the sqlite db
"""

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import os
import sqlite3


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
        
    
    def executeSql(self,sqlString, fieldNames=False):
        """
        calculate sql statement.
        
        returns 2 objects, list of fieldnames and list of tuple results. if fieldname not selected; returns None.
        """
        
        # execute sql
        self.curs.execute(sqlString)
        
        if fieldNames:
            # extract first item from tuple
            names = list(map(lambda x: x[0], self.curs.description))
            
            return names, self.curs.fetchall()
        else:
            # only return data
            return self.curs.fetchall()


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

    def joinAllCmpRows(self):
        """
        TODO: implement join all cmp table rows

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
        TODO: method to create tmp table populated with all joined rows for single slc from cmp table to snf

        create single tmp table to hold row results from single sl cmp join to snf table.

        slcId is int of slc to process.
        """

        pass


    # ========== categorical and numeric calculation methods
    """
    ** these methods must be generic enough to process single sl or the
    entire table of unique sl id's
    """

    def calculateField(self, slcIds, dbSlcKey="sl", tableName="cmp32", column="slope", dbPercentKey="percent"):
        """
        TODO: categorical calc -- update doc string
        
        dbSlcKey is column for slc id's.
        slcIds is any iterable object. 
        
        """
        
        # determine column data type
        # used to dispatch appriopate method to calculate
        def determineFieldDataType(tableName, column):
            """
            determine sqlite column data type. this ensures that characters such as #, _, - or "" not interpretted wrongly.
            in several cases first row that starts with them is a numeric field.
            
            uses sqlite pragma table_info to get sqlite column datatype assumptions. check user passed column against this table.
    
            return single value of "string" or "numeric"
            """
            
            # query sqlite pragma table_info
            sql = "pragma table_info(%s)" % (tableName)
            data = self.executeSql(sql)
    
            # match user column to sqlite field data returned from pragma
            # process tuples of this format (0, u'OGC_FID', u'INTEGER', 0, None, 1)
            fieldDataType = ""
            for row in data:
                if row[1] == column:
                    # match found. get sqlite field type
                    fieldDataType = row[2]
                    break
            
            # assume numeric field
            columnDataType = "numeric" 
            
            # check fieldType
            # sqlite provides either VARCHAR(2) or INTEGER/REAL
            if fieldDataType.startswith("VAR"):
                # text
                columnDataType = "string"
                
                print "found string"
                
                return columnDataType
            else:
                print "numeric"
                return columnDataType

                
        def categoricalCalculation(slcIds, dbSlcKey="sl", tableName="cmp32", column="slope", dbPercentKey="percent"):
            """
            - only show sub-dominate if dominate % < 60
            - % has no wieght on sub-dominate. take first one.
            - * check if result class = ""; replace with "NULL"
    
            calculates dominate/sub-dominate results for single string db field
    
            returns columns headers plus results.
            """
        
            # hold select dominate/sub-dominate data
            results = []
            
            for slcId in slcIds:
                # process each sl id separatly
            
                # summarize single sl id. determine count of categories present. rank by high-low.
                # dominate has highest count, sub-dominate is second highest.
                
                ## = examples
                ## select sl, dominate_category, dominate_weight from (select distinct(slope) as dominate_category,sl,sum(percent) as dominate_weight from cmp32 where sl = 254001 group by slope order by count(slope) desc limit 1) as  t
                ##sql = """select distinct(%s),count(%s) as count, sum(percent) as dominance from %s where %s = %s group by %s order by count(%s) desc""" %(dbSlcKey,column,column,tableName,dbSlcKey,slcId,column,column)
                
                sql = """select sl,dominate_category, dominate_weight from
                (select distinct(%s) as dominate_category, %s, sum(%s) as dominate_weight 
                from %s where %s = %s group by %s order by count(%s) desc limit 1) as t """ %(column,dbSlcKey,dbPercentKey, tableName, dbSlcKey, slcId,column,column)
                
                header, row = self.executeSql(sql,fieldNames=True)
                
                # only single row returned per slc. remove outer list to ensure we return a list of tuples.
                results.append(row[0])
                    
                
                #TODO: categorical calc -- check return sql values for "" and replace with nulls
            
                #TODO: categorical calc -- only show sub-dominate if dominate < 60%
            
                
            # return headers and results. headers will be last iteration.
            return header, results


        def numericCalculation(slcIds, dbSlcKey="sl", tableName="cmp32", column="slope", dbPercentKey="percent"):
            """
            TODO: field calc -- add to numeric doc string
    
            calculates weighted summed average of single numeric db field.
    
            returns sl ids,rows
            """
            
            # hold calculated sum weighted value
            results = []
            
            for slcId in slcIds:
                # process each sl id separatly
                
                ## = examples
                ## sql = """select distinct(sl) as sl, sum(%s * (percent/100.0)) as final from %s where sl = %s group by sl""" %(column,tableName,sl)
                
                sql ="""select distinct(%s) as %s, sum(%s * (%s/100.0)) as computed_value from %s where %s = %s group by %s""" % (dbSlcKey, dbSlcKey, column, dbPercentKey, tableName, dbSlcKey,  slcId, dbSlcKey)
                
                header, row = self.executeSql(sql,fieldNames=True)
                
                # only single row returned per slc. remove outer list to ensure we return a list of tuples.
                results.append(row[0])
                    
            
            # return headers and results. headers will be last iteration.
            return header, results

        
        #TODO: field calculation -- clean up. shouldn't need to cascade return values
        
        # dispatch to correct calculation method based on field data type
        if determineFieldDataType(tableName, column) == "string":
            # categorical column calculation
            print "Processing categorical calculation"
            headers, results = categoricalCalculation(slcIds, dbSlcKey="sl", tableName="cmp32", column="slope", dbPercentKey="percent")
            
            return headers, results
        
        elif determineFieldDataType(tableName, column) == "numeric":
            # numeric column calculation
            print "Processing numeric calculation"
            headers, results = numericCalculation(slcIds, dbSlcKey="sl", tableName="cmp32", column="slope", dbPercentKey="percent")
            
            return headers, results
        
        else:
            # error
            #TODO: calculation -- if issue determining column data type report error
            pass
            
    
    # ========== demos

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
        print results


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



