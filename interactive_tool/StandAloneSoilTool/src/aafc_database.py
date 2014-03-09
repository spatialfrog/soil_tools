"""
handles all interactions with the sqlite db
"""

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import os
import sqlite3
##from aafc_workflow import dbCmpKey, dbLayerNumberKey


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
    
    
    def prefixDbTableColumns(self, tableName):
        """
        prefix table name ie cmp to each column ie cmp_sl
        
        ensures when join occurs, it is clear what column table is from. *ensures that duplicate column names not prepended with :1 from sqlite.
        
        updates original table with new column names.
        """
        
        #TODO: nice to have -- prefix db table columns names
        
        """
        sqlite does not provide alter column name command. either have to recreate target table with cleaned up names and insert data into
        or update sqlite_master table (http://www.gfairchild.com/2012/08/03/how-to-rename-columns-in-an-sqlite-database/)
        """
        
        # pragma of table_info on user supplied table name
        sql = "pragma table_info(%)" %(tableName)
        results = self.executeSql(sql)
        
        # second column contains field names (0, u'OGC_FID', u'INTEGER', 0, None, 1)
        tmpNames = []
        for i in results:
            # append table name as prefix separated from column name with underscore
            columnName = tableName + "_" + i[1]
            tmpNames.append(columnName)
        
        # update db table with new names
        
        pass
    


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

    def resultsTableJoiningCmpSnfBySoilkey(self,slcIds, dbSlcKey, dbCmpKey, dbSoilKey, cmpTableName, snfTableName, landuse, writeTestCsv=False, writeTestCsvDirectory=None):
        """
        provide cmp soilkey to match landuse on.

        strip soilkey of last character. search snf table for all matches.
        if landuse character present in table soilkey; return soilkey; else
        return avaibale soilkey.
        """
        
        #TODO: refactor 2 table & 3 table join methods into single method
        
        resultsTableName = "results_joinedCmpSnf"
            
        def processSlcRows(slcIds, dbSlcKey, dbCmpKey, dbSoilKey, cmpTableName, snfTableName, landuse, resultsTableName):
            """
            process slc ids and insert data into flat results table
            
            returns list of messages used for testing
            """
            
            resultsTableCreated = False
            
            # captures key results that will be added and written to csv only if writeTextCsv = True
            messagesTestCsv = []
            messagesTestCsv.append(("///// land use preference is %s\n\n\n"%(landuse)))
                    
            # process slc ids
            for slcId in slcIds:
                # process each row within given sl.
                # get cmp count. int id from 1 to n. cmp id will allow unique row id within sl
                sql = "select %s from %s where %s = %s" %(dbCmpKey, cmpTableName, dbSlcKey, slcId)
                results = self.executeSql(sql)
                
                messagesTestCsv.append(("===== slc %s being processed \n" %(slcId)))
                
                # iterate over every cmp number
                for i in results:
                    # extract cmp id from tuple
                    cmpId = i[0]
                    
                    # return soil key column for cmp + sl
                    sql = "select %s from %s where %s = %s and %s = %s" %(dbSoilKey, cmpTableName, dbSlcKey, slcId, dbCmpKey, cmpId)
                    result = self.executeSql(sql)
                    
                    msg = "cmp row %s from component table soilkey is %s\n" %(cmpId, result)
                    messagesTestCsv.append(msg)
                    
                    # find soil key matches avaibale in snf table to user by stripping supplied soil key from cmp table row
                    # strip end landuse from provided key & append %. used for sql character matching
                    strippedCmpSoilTableKey = (result[0][0])[:-1] + "%"
                    
                    # get distinct matches of sl cmp soil keys in snf table
                    sql = "select distinct(%s) from %s where %s like '%s'" %(dbSoilKey, snfTableName, dbSoilKey, strippedCmpSoilTableKey)
                    results = self.executeSql(sql)
                    
                    msg = "slf table distinct soilkeys are %s\n" %(results)
                    messagesTestCsv.append(msg)
                    
                    # is user landuse preference availabe
                    # check end character of string; if matches user then select key else use default of N
                    snfSoilKeyToUse = ""
                    
                    for e in results:
                        # convert to lowercase for checking
                        eToLowerCase = e[0].lower()    
                        if eToLowerCase.endswith(landuse.lower()):
                            # user land preference can be accomindated
                            snfSoilKeyToUse = e[0]
                            break
                        else:
                            # only one soil key in snf. must use this
                            snfSoilKeyToUse = e[0]
                            messagesTestCsv.append(("* Can't accomindate land use preference"))
                    
                    msg = "snf soilkey to us is %s\n" %(snfSoilKeyToUse)
                    messagesTestCsv.append(msg)
                    msg = "----------\n\n"
                    messagesTestCsv.append(msg)
                    
                    if not resultsTableCreated:
                        # table does not exist
                        # create table
                        sql = "create table %s as select * from %s join %s on %s.%s like '%s' and %s.%s = %s and %s.%s = %s" %(resultsTableName, cmpTableName, snfTableName, snfTableName, dbSoilKey, snfSoilKeyToUse, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId)
                        self.executeSql(sql)
                        
                        # commit transaction
                        self.conn.commit()
                        
                        # flaf that table has been created
                        resultsTableCreated = True
                
                    #== insert data into table
                    # join cmp32 sl row to snf row with soilkey match. return all columns from both tables.
                    # cmp32 cmp id constrains to create unique row id for cmp32.
                    sql = "insert into %s select * from %s join %s on %s.%s like '%s' and %s.%s = %s and %s.%s = %s" %(resultsTableName, cmpTableName, snfTableName, snfTableName, dbSoilKey, snfSoilKeyToUse, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId)
                    self.executeSql(sql)
                     
                # commit transaction
                self.conn.commit()
        
            # return list of messages
            return messagesTestCsv

        # drop results table
        sql = "drop table if exists %s" %(resultsTableName)
        self.executeSql(sql)
        
        # create new results table with join results inserted for each slc id row
        messages = processSlcRows(slcIds, dbSlcKey, dbCmpKey, dbSoilKey, cmpTableName, snfTableName, landuse, resultsTableName)
        
        # write test csv output if writeTestCsv requested
        if writeTestCsv:
            with open(os.path.join(writeTestCsvDirectory, "test_2_tableJoin.txt"),"w") as file_open:
                for msg in messages:
                    file_open.writelines(msg)
                    file_open.write("\n")
        
        
    
    def resultsTableJoiningCmpSnfSlfBySoilkey(self,slcIds, dbSlcKey, dbCmpKey, dbSoilKey, dbLayerNumberKey, cmpTableName, snfTableName, slfTableName, landuse, layerNumber, writeTestCsv=False, writeTestCsvDirectory=None):
        """
        joins all 3 soil tables, cmp -- snf -- slf table together based on single distinct sl from cmp with common soilkey and single slf layer number.
        
        if slf layer number not present for row being evaluated, that row is dropped from resultant table.
        """
    
        ##-- sql example -- join all three tables
        ##-- join cmp & snf first to get soilkey to be used, join cmp row selected against slf table constrained by layer number
        ##select cmp32.sl, cmp32.soilkey as cmp32_soilkey, snf32.drainage, slf32.* from cmp32 join snf32 on snf32.soilkey like 'ABBUFgl###N' and cmp32.sl = 242021 and cmp32.cmp = 1 join slf32 on cmp32.soilkey like slf32.soilkey and slf32.layer_no = 2
        
        resultsTableName = "results_joinedCmpSnfSnl"
            
        def processSlcRows(slcIds, dbSlcKey, dbCmpKey, dbSoilKey, dbLayerNumberKey, cmpTableName, snfTableName, slfTableName, landuse, layerNumber):
            """
            process slc ids and insert data into flat results table
            """
            
            resultsTableCreated = False
            # captures key results that will be added and written to csv only if writeTextCsv = True
            messagesTestCsv = []
            messagesTestCsv.append(("///// land use preference is %s\n\n"%(landuse)))
            messagesTestCsv.append("/////  layer number is %s\n\n"%(layerNumber))
                        
            # process slc ids
            for slcId in slcIds:
                # process each row within given sl.
                # get cmp count. int id from 1 to n. cmp id will allow unique row id within sl
                sql = "select %s from %s where %s = %s" %(dbCmpKey, cmpTableName, dbSlcKey, slcId)
                results = self.executeSql(sql)
                
                messagesTestCsv.append(("===== slc %s being processed \n" %(slcId)))
                
                # iterate over every cmp number
                for i in results:
                    # extract cmp id from tuple
                    cmpId = i[0]
                    
                    # return soil key column for cmp + sl
                    sql = "select %s from %s where %s = %s and %s = %s" %(dbSoilKey, cmpTableName, dbSlcKey, slcId, dbCmpKey, cmpId)
                    result = self.executeSql(sql)
                    
                    msg = "cmp row %s from component table soilkey is %s\n" %(cmpId, result)
                    messagesTestCsv.append(msg)
                    
                    # find soil key matches avaibale in snf table to user by stripping supplied soil key from cmp table row
                    # strip end landuse from provided key & append %. used for sql character matching
                    strippedCmpSoilTableKey = (result[0][0])[:-1] + "%"
                    
                    # get distinct matches of sl cmp soil keys in snf table
                    sql = "select distinct(%s) from %s where %s like '%s'" %(dbSoilKey, snfTableName, dbSoilKey, strippedCmpSoilTableKey)
                    results = self.executeSql(sql)
                    
                    msg = "slf table distinct soilkeys are %s\n" %(results)
                    messagesTestCsv.append(msg)
                    
                    # is user landuse preference availabe
                    # check end character of string; if matches user then select key else use default of N
                    snfSoilKeyToUse = ""
                    
                    for e in results:
                        # convert to lowercase for checking
                        eToLowerCase = e[0].lower()    
                        if eToLowerCase.endswith(landuse.lower()):
                            # user land preference can be accomindated
                            snfSoilKeyToUse = e[0]
                            break
                        else:
                            # only one soil key in snf. must use this.
                            snfSoilKeyToUse = e[0]
                            messagesTestCsv.append(("* Can't accomindate land use preference"))
                    
                    msg = "snf soilkey to us is %s\n" %(snfSoilKeyToUse)
                    messagesTestCsv.append(msg)
                    
                    # join slf table based on soil key and layer number
                    # check if user requested snl layer number is avaiable. if not, disgard slc id and process next one
                    snlLayerNumberToUse = ""
                    snlLayerNumberFound = False
                    
                    # get distinct layer numbers in snl table based on snf soilkey to be used
                    sql = "select distinct(%s) from %s where %s like '%s'" %(dbLayerNumberKey, slfTableName, dbSoilKey, snfSoilKeyToUse)
                    results = self.executeSql(sql)
                    
                    msg = "distinct snl layer numbers are %s\n" %(results)
                    messagesTestCsv.append(msg)
                    
                    # is user requested slf layer number available
                    for e in results:
                        if e[0] == layerNumber:
                            # match
                            snlLayerNumberToUse = e[0]
                            snlLayerNumberFound = True
                            messagesTestCsv.append((">>> user requested soil layer in slf table found\n\n----------\n"))
                            break
                    
                    # user layer number missing. drop this slc id + cmp row. process next slc id + cmp row
                    if snlLayerNumberFound == False:    
                        msg = "* slf layer number not found. skipping current slc id + cmp row. will try next row.\n\n----------\n"
                        messagesTestCsv.append(msg)
                        break    
                    
                    # process join
                    if not resultsTableCreated:
                        # table does not exist
                        # create table
                        sql = "create table %s as select * from %s join %s on %s.%s like '%s' and %s.%s = %s and %s.%s = %s join %s on %s.%s like %s.%s and %s.%s = %s" %(resultsTableName, cmpTableName, snfTableName, snfTableName, dbSoilKey, snfSoilKeyToUse, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId, slfTableName, cmpTableName, dbSoilKey, slfTableName, dbSoilKey, slfTableName, dbLayerNumberKey, snlLayerNumberToUse)
                        self.executeSql(sql)
                        
                        # commit transaction
                        self.conn.commit()
                        
                        # flaf that table has been created
                        resultsTableCreated = True
                    
                    #== insert data into table
                    # join cmp sl row to snf row and slf row with soilkey and layer number match. return all columns from tables
                    # cmp cmp id constrains to create unique row id for cmp
                    sql = "insert into %s select * from %s join %s on %s.%s like '%s' and %s.%s = %s and %s.%s = %s join %s on %s.%s like %s.%s and %s.%s = %s" %(resultsTableName, cmpTableName, snfTableName, snfTableName, dbSoilKey, snfSoilKeyToUse, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId, slfTableName, cmpTableName, dbSoilKey, slfTableName, dbSoilKey, slfTableName, dbLayerNumberKey, snlLayerNumberToUse)
                    self.executeSql(sql)
                     
                # commit transaction
                self.conn.commit()

            return messagesTestCsv

        # drop results table
        sql = "drop table if exists %s" %(resultsTableName)
        self.executeSql(sql)
        
        # create new results table with join results inserted for each slc id row
        messages = processSlcRows(slcIds, dbSlcKey, dbCmpKey, dbSoilKey, dbLayerNumberKey, cmpTableName, snfTableName, slfTableName, landuse, layerNumber)
        
        # write test csv output if writeTestCsv requested
        if writeTestCsv:
            with open(os.path.join(writeTestCsvDirectory, "test_3_tableJoin.txt"),"w") as file_open:
                for msg in messages:
                    file_open.writelines(msg)
                    file_open.write("\n")
    
    
    # ========== categorical and numeric calculation methods
    """
    ** these methods must be generic enough to process single sl or the
    entire table of unique sl id's
    """

    def calculateField(self, slcIds, dbSlcKey, tableName, columnName, dbPercentKey):
        """
        TODO: categorical calc -- update doc string
        
        dbSlcKey is column for slc id's.
        slcIds is any iterable object. 
        
        """
        
        # determine column data type
        # used to dispatch appriopate method to calculate
        def determineFieldDataType(tableName, columnName):
            """
            determine sqlite column data type. this ensures that characters such as #, _, - or "" not interpretted wrongly.
            in several cases first row that starts with them is a numeric field.
            
            uses sqlite pragma table_info to get sqlite column datatype assumptions. check user passed column against this table.
    
            return single value of "string" or "numeric"
            """
            
            # data type from sqlite for user supplied column
            columnDataType = "" 

            # query sqlite pragma table_info
            sql = "pragma table_info(%s)" % (tableName)
            data = self.executeSql(sql)
                
            # match user column to sqlite field data returned from pragma
            # process tuples of this format (0, u'OGC_FID', u'INTEGER', 0, None, 1)
            fieldDataType = ""
            for row in data:
                # remove double quote within single quote if present. only passed if db column name is duplicate ie '"slope:2"'
                columnNameStripped = columnName.strip('\"')
                if row[1].lower() == columnNameStripped.lower():
                    # match found. get sqlite field type
                    fieldDataType = row[2]
                    break
            
            
            # check fieldType
            # sqlite provides either VARCHAR/TEXT or INTEGER/REAL
            # convert fieldtype to lower to check
            if fieldDataType.lower().startswith("var") or fieldDataType.lower().startswith("tex"):
                # text
                columnDataType = "string"
                return columnDataType
            elif fieldDataType.lower().startswith("int") or fieldDataType.lower().startswith("rea"):
                columnDataType = "numeric"
                return columnDataType
            else:
                print "could not match data type!!"
            

                
        def categoricalCalculation(slcIds, dbSlcKey, tableName, columnName, dbPercentKey):
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
                from %s where %s = %s group by %s order by count(%s) desc limit 1) as t """ %(columnName,dbSlcKey,dbPercentKey, tableName, dbSlcKey, slcId,columnName,columnName)
                
                header, row = self.executeSql(sql,fieldNames=True)
                
                #TODO: ** critical -- check if any value returned - categorical
                if len(row) == 0:
                    # no data returned
                    pass
                else:
                    # only single row returned per slc. remove outer list to ensure we return a list of tuples.
                    results.append(row[0])
                    
                
                #TODO: categorical calc -- check return sql values for "" and replace with nulls
            
                #TODO: categorical calc -- only show sub-dominate if dominate < 60%
            
                
            # return headers and results. headers will be last iteration.
            return header, results


        def numericCalculation(slcIds, dbSlcKey, tableName, columnName, dbPercentKey):
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
                ## select distinct(sl) as sl, sum(awhc_v * (percent/100.0)) as final from cmp32 where sl = 376002 group by sl
                ## sql = """select distinct(sl) as sl, sum(%s * (percent/100.0)) as final from %s where sl = %s group by sl""" %(column,tableName,sl)
                
                sql ="""select distinct(%s) as %s, sum(%s * (%s/100.0)) as weighted_average from %s where %s = %s group by %s""" % (dbSlcKey, dbSlcKey, columnName, dbPercentKey, tableName, dbSlcKey,  slcId, dbSlcKey)
                header, row = self.executeSql(sql,fieldNames=True)
                
                
                #TODO: ** critical -- check if any value returned - numeric
                if len(row) == 0:
                    # no data returned
                    pass
                else:
                    #== format numeric calc in db tuple before passing back
                    # format calculated value to 2 decimal places
                    formattedNumber = (row[0][0],"{:0.2f}".format(round(row[0][1],2)))
                    
                    # only single row returned per slc. remove outer list to ensure we return a list of tuples.
                    results.append(formattedNumber)
                    
            
            # return headers and results. headers will be last iteration.
            return header, results

        
        #TODO: field calculation -- clean up. shouldn't need to cascade return values
        
        # determine column field data type
        columnDataTypeIs = determineFieldDataType(tableName, columnName)
        
        # dispatch to correct calculation method based on field data type
        if columnDataTypeIs == "string":
            # categorical column calculation
            headers, results = categoricalCalculation(slcIds, dbSlcKey, tableName, columnName, dbPercentKey)
            
            return headers, results
        
        elif columnDataTypeIs == "numeric":
            # numeric column calculation
            headers, results = numericCalculation(slcIds, dbSlcKey, tableName, columnName, dbPercentKey)
            
            return headers, results
        
        else:
            # error
            #TODO: calculation -- if issue determining column data type report error
            print "mmmm couldn't figure out column type"
            print columnDataTypeIs

