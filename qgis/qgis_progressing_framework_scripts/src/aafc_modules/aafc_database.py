"""
purpose:
handles all interactions with the sqlite db

how:
python sqlite3 module

notes:
cmp32 is base table for all quieries. must go in order of cmp32 -- snf32 -- slf32.
soilkey is pk in cmp and fk in other 2 tables.

** for a single SLC polygon, we join all soilkeys from cmp table to the other tables.

if snf, must choose either landuse of A or N; if A absent then assume N. 1:2 relationship possible between cmp soilkey.
* strip the N/A off cmp soilkey and search snf soilkey with N/A also stripped. if user specified N/A found;
  join on that; else default to the avaiable landuse N/A soilkey.

if slf, user can only select 1 layer number. 1:many between soilkey.
slf layer_no appears to be layer number.

license:
gpl3

developer:
richard burcher
richardburcher@gmail.com
2014
"""

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import os
import sqlite3
import time
from multiprocessing import Pool


class Db:
    """
    purpose:
    handles all db activities
    
    notes:
    -there is only one method that executes sql "self.executeSql()"
    """

    def __init__(self, sqliteDbPath, tmpSystemDirectory):
        # db path
        self.sqliteDbPath = sqliteDbPath

        # db connection
        self.conn = sqlite3.connect(sqliteDbPath)
        self.curs = self.conn.cursor()

        # temp system directory
        self.tmpDirectory = tmpSystemDirectory
        
        # join table name. generic as you can only have 1 join table at a time
        self.joinTableName = "joinedSoilTables"
        
        # user options table name for possible joins allowed
        self.userJoinOptionsTable = "possibleJoinsToCreate"
        
        # has join table been created
        self.resultsTableCreated = False
        
        # log file
        self.messagesTestCsv = []
        
    
    def executeSql(self,sqlString, fieldNames=False, multipleSqlString=False):
        """
        purpose:
        main point of sql interaction with db
        
        returns:
        either data only list of tuples; default or a list of fieldnames and list of tuple results
        """

        # multiple sql statements to process
        if multipleSqlString:
            #TODO: split list into 2 maybe n lists and process separately to speed up inserts. would need additional db connections            
            returnData = []
            for e in sqlString: 
                # execute sql
                self.curs.execute(e)
                #TODO: implement cleaned up return values
                # clean up data to be simple list
                cleanedData = list(self.curs.fetchall())
                if fieldNames:
                    # extract first item from tuple
                    names = list(map(lambda x: x[0], self.curs.description))
                     
                    returnData.append([names, cleanedData])
                else:
                    # only return data
                    returnData.append(cleanedData)
            # return data
            return returnData
            
        else:
            #===== single sql string to process
            # execute sql
            self.curs.execute(sqlString)
            
            if fieldNames:
                # extract first item from tuple
                names = list(map(lambda x: x[0], self.curs.description))
                
                return names, self.curs.fetchall()
            else:
                # only return data
                return self.curs.fetchall()


    def createDbIndexesOnJoinedTable(self):
        """
        purpose:
        create sqlite indexes on all columns in the joined table
        
        how:
        sql
        
        notes:
        -tableNames must be iterable
        -used to speed up joins
        
        returns:
        nothing
        """
        
        # get table listing for joined table
        tableNames = self.getTableFieldNames(self.joinTableName)
        
        for tableName in tableNames:
            # clean up table names that had :1 or :2 in them. results from duplicate tables
            cleanedTableName = tableName.replace(":","_")
            # create sql for index
            sql = "create index index_%s_%s on %s('%s')" % (self.joinTableName, cleanedTableName, self.joinTableName, tableName)
            self.executeSql(sql)
        
        # analyze db to generate stats for query planner
        self.executeSql("ANALYZE")


    def createDbIndexesOnLoadedData(self, tableNames, dbSoilKey, dbSlcId, dbCmpKey, dbPercentKey, dbLayerNumberKey):
        """
        purpose:
        create sqlite indexes on the loaded dbf soil db columns
        
        how:
        sql
        
        notes:
        -tableNames must be iterable
        -used to speed up joins
        
        returns:
        nothing
        """
        
        for tableName in tableNames:
            if tableName == "cmp":
                # add cmp specific indexes
                # soilkey/soilmap
                sql = "create index index_cmp_soilkey on cmp(%s)" % (dbSoilKey)
                self.executeSql(sql)
                # percent column
                sql = "create index index_cmp_percent on cmp(%s)" % (dbPercentKey)
                self.executeSql(sql)
                # slc id 
                sql = "create index index_cmp_slcid on cmp(%s)" % (dbSlcId)
                self.executeSql(sql)
                # cmp id
                sql = "create index index_cmp_cmpid on cmp(%s)" % (dbCmpKey)
                self.executeSql(sql)
            elif tableName == "snf":
                # snf indexes
                # soilkey/soilmap
                sql = "create index index_snf_soilkey on snf(%s)" % (dbSoilKey)
                self.executeSql(sql)
            elif tableName == "slf":
                # slf specific keys
                # soilkey/soilmap
                sql = "create index index_slf_soilkey on slf(%s)" % (dbSoilKey)
                self.executeSql(sql)
                # layer number
                sql = "create index index_slf_layernumber on slf(%s)" % (dbLayerNumberKey)
                self.executeSql(sql)
        
        # analyze db to generate stats for query planner
        self.executeSql("ANALYZE")
    
    
    def sqliteLoadingPerformanceTuning(self, enable=True, closeDbConnection=False):
        """
        purpose:
        increase db performance when loading data
        
        notes:
        turns off journal mode and synchronous modes
        see http://www.sqlite.org/pragma.html
        
        returns:
        nothing
        """
        
        if enable:
            # turn off journal mode
            sql="pragma journal_mode=OFF"
            self.executeSql(sql)
            # turn off synchronous mode
            sql="pragma synchronous=OFF"
            self.executeSql(sql)
            # increase page size
            sql="pragma page_size=8192"
            self.executeSql(sql)
            # increase cache_size
            sql = "pragma cache_size=100000"
            self.executeSql(sql)
            # must vacuum for page_size to be used
            self.executeSql("VACUUM")
        else:
            # turn back on
            # turn on journal mode
            sql="pragma journal_mode=MEMORY"
            self.executeSql(sql)
            # turn on synchronous mode
            sql="pragma synchronous=NORMAL"
            self.executeSql(sql)
            # set page size default
            sql="pragma page_size=1024"
            self.executeSql(sql)
            # must vacuum for page_size to be used
            self.executeSql("VACUUM")
        
        # close db connection
        if closeDbConnection:
            self.conn.close()
        
        

    def convertDbResults2SimpleList(self,data, columnIndex=0):
        """
        purpose:
        convert db query data from list of tuples into simple list
        
        returns:
        returns list
        """
        
        results = []
        for i in data:
            # extract single value from tuple
            results.append((i[columnIndex]))
        
        return results


    def updateDbTableName(self,tableName):
        """
        purpose:
        sql update name of initial loaded cmp table
        
        notes:
        when db created, table name is set to db file name. set this to the passed in table name.
        
        returns:
        nothing
        """

        # get basename of db path minus extension
        tmp = os.path.splitext(os.path.basename(self.sqliteDbPath))[0]
        # convert to lowercase. sqlite tables are all lower.
        baseDbName = tmp.lower()

        # update table name via sql
        sql = "alter table %s rename to %s" % (baseDbName,tableName)
        results = self.executeSql(sql)
    
    
    def dropTable(self,tableName):
        """
        purpose:
        db convience method to drop table
        
        notes:
        drops table name from user supplied table name
        
        returns:
        nothing
        """
        
        sql = "drop table if exists %s" %(tableName)
        self.executeSql(sql)
    
    
    def getSoilTablesListing(self):
        """
        purpose:
        gets listing of user loaded soil tables
        
        how:
        searches for cmp/slf/snf names
        
        returns:
        list of soil table name strings
        """
        
        # list of tables in db
        sql = "select name from sqlite_master where type='table'"
        results = self.executeSql(sql)
        
        # clean data into simple list
        cleanedResults = self.convertDbResults2SimpleList(results)
        
        # search for soil names
        soilTableNames = ["cmp","snf","slf"]
        
        soilTablesPresent = []
        
        for soilName in soilTableNames:
            for tableName in cleanedResults:
                if soilName.lower() in tableName.lower():
                    # match
                    soilTablesPresent.append(soilName)
                    continue
        
        return soilTablesPresent 


    def getTableFieldNames(self, tableName):
        """
        purpose:
        return listing of field names present in user supplied table
        
        how:
        sqlite pragma table_info
        
        returns:
        list of all field names
        """
        
        # list db fields
        sql = "pragma table_info(%s)" %(tableName)
        results = self.executeSql(sql)
        
        # clean results. field name is second index position
        cleanedResults = self.convertDbResults2SimpleList(results, columnIndex=1)
        
        return cleanedResults
        
    
    def createUserTableProcessingOptions(self, tableOptions):
        """
        purpose:
        create new table that will be used in downstream qgis script for user to select what tables to use for joining
        
        how:
        passed in dict values contains table formated options ie cmp, cmp-snf or cmp-snf-slf
        
        returns:
        nothing
        """
        
        # drop table if present
        sql = "drop table if exists %s" %(self.userJoinOptionsTable)
        self.executeSql(sql)
        
        # check for highest key order to create table and insert statement
        if tableOptions.get(2,None):
            print "processing"
            sql = "create table %s('cmp-snf' INTEGER, 'cmp-snf-slf' INTEGER)" %(self.userJoinOptionsTable)
            self.executeSql(sql)
            sql = "insert into %s('cmp-snf', 'cmp-snf-slf') values(1, 2)" %(self.userJoinOptionsTable)
            self.executeSql(sql)
            self.conn.commit()
        elif tableOptions.get(1,None):
            print "processing"
            sql = "create table %s('cmp-snf' INTEGER)" %(self.userJoinOptionsTable)
            self.executeSql(sql)
            sql = "insert into %s('cmp-snf') values(1)" %(self.userJoinOptionsTable)
            self.executeSql(sql)
            self.conn.commit()
    
    
    #//////////////////// table joins    
    
    def resultsTableJoiningCmpSnfBySoilkey(self,slcIds, dbSlcKey, dbCmpKey, dbSoilKey, cmpTableName, snfTableName, landuse, writeTestCsv=False, writeTestCsvDirectory=None):
        """
        purpose:
        create join between cmp and snf soil tables
        
        notes:
        -join is based on slc ids supplied and soilkey
        -strip soilkey of last character. search snf table for all matches. if landuse character present in table soilkey; return soilkey; else return avaibale soilkey
        -* all inserts done when slc ids processed. create sequence of slq insert strings that are processed at end
        
        returns:
        nothing
        """
        
        #TODO: nice to do -- refactor 2 table & 3 table join methods into single method
        
        resultsTableName = self.joinTableName
            
        def processSlcRows(slcIds, dbSlcKey, dbCmpKey, dbSoilKey, cmpTableName, snfTableName, landuse, resultsTableName):
            """
            process slc ids and insert data into flat results table
            
            returns list of messages used for testing
            """
            
            resultsTableCreated = False
            
            # captures key results that will be added and written to csv only if writeTextCsv = True
            self.messagesTestCsv = []
            self.messagesTestCsv.append(("///// land use preference is %s\n\n\n"%(landuse)))
            self.messagesTestCsv.append(("start time is %s" %(time.ctime(time.time()))))
            
            
            # get all soil keys from snf table
            sql = "select distinct(%s) from %s" %(dbSoilKey, snfTableName)
            results = self.executeSql(sql)
            snfSoilKeys = []
            # clean up into simple list of strings
            for e in results:
                snfSoilKeys.append(e[0])
             
            # sql insert string. string holds all inserts per slc id & at end inserts into db
            sqlInserts = []
            
            # process slc ids
            for slcId in slcIds:
                # process each row within given sl
                
                # create data structure from sql query once for each sl processed. list of tuples containing (sl, cmp, soilkey). access via index
                # query db cmp table for sl, cmp, soilkey
                sql = "select %s, %s, %s from %s where %s = %s" %(dbSlcKey, dbCmpKey, dbSoilKey, cmpTableName, dbSlcKey, slcId)
                results = self.executeSql(sql) 
                
                # process
                for item in results:
                    slcId = item[0]
                    cmpId = item[1]
                    soilKeyToUse = item[2]
                    
                    # is user landuse preference availabe
                    # check end character of string; if matches user then select key else use default of N
                    snfSoilKeyToUse = ""
                    
                    #////// only for output diagnostic csv
                    # get list of snf soil keys present that match cmp soil key
                    snfDistinctKeysMsg = []
                    if soilKeyToUse[:-1] + landuse in snfSoilKeys:
                        # user landuse preference can be accomidated
                        snfDistinctKeysMsg.append((soilKeyToUse[:-1] + landuse))
                        
                    if soilKeyToUse[:-1] + "N" in snfSoilKeys:
                        # default landuse of N
                        snfDistinctKeysMsg.append((soilKeyToUse[:-1] + "N"))
                    
                    self.messagesTestCsv.append("snf soil keys: %s" %(snfDistinctKeysMsg))
                    # //////////
                    
                    # match cmp soil key to snf soil and respect user land use preference if possible 
                    # strip off last character of cmp soil key. add user landuse and check if in snf soilkey list
                    if soilKeyToUse[:-1] + landuse in snfSoilKeys:
                        # user landuse preference can be accomidated
                        snfSoilKeyToUse = soilKeyToUse[:-1] + landuse
                        self.messagesTestCsv.append(("Can accomindate land use preference"))
                    elif soilKeyToUse[:-1] + "N" in snfSoilKeys:
                        # default landuse of N
                        snfSoilKeyToUse = soilKeyToUse[:-1] + "N"
                        self.messagesTestCsv.append(("* Can't accomindate land use preference"))
                    
                    
                    if not resultsTableCreated:
                        # table does not exist
                        # create table                        
                        ## example
                        #select * from cmp, snf where cmp.sl = 242021 and cmp.cmp = 1 and snf.soilkey = 'ABBUFgl###N'
                        sql = "create table %s as select * from %s, %s where %s.%s = %s and %s.%s = %s and %s.%s = '%s'" %(resultsTableName, cmpTableName, snfTableName, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId, snfTableName, dbSoilKey, snfSoilKeyToUse)
                        self.executeSql(sql)
                        
                        # commit transaction to create table
                        self.conn.commit()
                        
                        # flag that table has been created
                        resultsTableCreated = True
                    else:
                        # create sql insert strings
                        sql = "insert into %s select * from %s, %s where %s.%s = %s and %s.%s = %s and %s.%s = '%s'" %(resultsTableName, cmpTableName, snfTableName, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId, snfTableName, dbSoilKey, snfSoilKeyToUse)
                        sqlInserts.append(sql)
                    
            self.messagesTestCsv.append(("start sql inserts: time is %s" %(time.ctime(time.time()))))
            # process all sql insert statements for slc ids
            self.executeSql(sqlInserts, multipleSqlString=True)
            self.messagesTestCsv.append(("finished sql inserts: time is %s" %(time.ctime(time.time()))))
                     
            # commit transaction
            self.conn.commit()
                
            self.messagesTestCsv.append(("all finished -- db commit finished: time is %s" %(time.ctime(time.time()))))
        
            # return list of messages
            return self.messagesTestCsv

        # drop join table
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
        purpose:
        create 3 table join between cmp/snf/slf soil tables
        
        notes:
        -join based on single distinct sl from cmp with common soilkey and single slf layer number
        -if slf layer number not present for row being evaluated, that row is dropped from resultant table
        
        returns:
        nothing
        """
    
        ##-- sql example -- join all three tables
        ##-- join cmp & snf first to get soilkey to be used, join cmp row selected against slf table constrained by layer number
        ##select cmp32.sl, cmp32.soilkey as cmp32_soilkey, snf32.drainage, slf32.* from cmp32 join snf32 on snf32.soilkey like 'ABBUFgl###N' and cmp32.sl = 242021 and cmp32.cmp = 1 join slf32 on cmp32.soilkey like slf32.soilkey and slf32.layer_no = 2
                
        resultsTableName = self.joinTableName
            
        def processSlcRows(slcIds, dbSlcKey, dbCmpKey, dbSoilKey, dbLayerNumberKey, cmpTableName, snfTableName, slfTableName, landuse, layerNumber):
            """
            process slc ids and insert data into flat results table
            
            returns list of messages used for testing
            """
            
            resultsTableCreated = False
            
            # captures key results that will be added and written to csv only if writeTextCsv = True
            messagesTestCsv = []
            messagesTestCsv.append(("///// land use preference is %s\n\n\n"%(landuse)))
            messagesTestCsv.append(("start time is %s" %(time.ctime(time.time()))))
            
            
            # get all soil keys from snf table
            sql = "select distinct(%s) from %s" %(dbSoilKey, snfTableName)
            results = self.executeSql(sql)
            snfSoilKeys = []
            # clean up into simple list of strings
            for e in results:
                snfSoilKeys.append(e[0])
             
            # sql insert string. string holds all inserts per slc id & at end inserts into db
            sqlInserts = []
            
            # process slc ids
            for slcId in slcIds:
                # process each row within given sl
                
                # create data structure from sql query once for each sl processed. list of tuples containing (sl, cmp, soilkey). access via index
                # query db cmp table for sl, cmp, soilkey
                sql = "select %s, %s, %s from %s where %s = %s" %(dbSlcKey, dbCmpKey, dbSoilKey, cmpTableName, dbSlcKey, slcId)
                results = self.executeSql(sql) 
                
                # process
                for item in results:
                    slcId = item[0]
                    cmpId = item[1]
                    soilKeyToUse = item[2]
                    
                    # is user landuse preference availabe
                    # check end character of string; if matches user then select key else use default of N
                    snfSoilKeyToUse = ""
                    
                    #////// only for output diagnostic csv
                    # get list of snf soil keys present that match cmp soil key
                    snfDistinctKeysMsg = []
                    if soilKeyToUse[:-1] + landuse in snfSoilKeys:
                        # user landuse preference can be accomidated
                        snfDistinctKeysMsg.append((soilKeyToUse[:-1] + landuse))
                        
                    if soilKeyToUse[:-1] + "N" in snfSoilKeys:
                        # default landuse of N
                        snfDistinctKeysMsg.append((soilKeyToUse[:-1] + "N"))
                    
                    messagesTestCsv.append("snf soil keys: %s" %(snfDistinctKeysMsg))
                    # //////////
                    
                    # match cmp soil key to snf soil and respect user land use preference if possible 
                    # strip off last character of cmp soil key. add user landuse and check if in snf soilkey list
                    if soilKeyToUse[:-1] + landuse in snfSoilKeys:
                        # user landuse preference can be accomidated
                        snfSoilKeyToUse = soilKeyToUse[:-1] + landuse
                        messagesTestCsv.append(("Can accomindate land use preference"))
                    elif soilKeyToUse[:-1] + "N" in snfSoilKeys:
                        # default landuse of N
                        snfSoilKeyToUse = soilKeyToUse[:-1] + "N"
                        messagesTestCsv.append(("* Can't accomindate land use preference"))
                    
                    
                    #//////
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
                    else:
                        #== insert data into table
                        # join cmp sl row to snf row and slf row with soilkey and layer number match. return all columns from tables
                        # cmp cmp id constrains to create unique row id for cmp
                        sql = "insert into %s select * from %s join %s on %s.%s like '%s' and %s.%s = %s and %s.%s = %s join %s on %s.%s like %s.%s and %s.%s = %s" %(resultsTableName, cmpTableName, snfTableName, snfTableName, dbSoilKey, snfSoilKeyToUse, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId, slfTableName, cmpTableName, dbSoilKey, slfTableName, dbSoilKey, slfTableName, dbLayerNumberKey, snlLayerNumberToUse)
                        ##self.executeSql(sql)
                        sqlInserts.append(sql)
            
            
            messagesTestCsv.append(("start sql inserts: time is %s" %(time.ctime(time.time()))))
            # process all sql insert statements for slc ids
            self.executeSql(sqlInserts, multipleSqlString=True)
            messagesTestCsv.append(("finished sql inserts: time is %s" %(time.ctime(time.time()))))
                    
            # commit transaction
            self.conn.commit()

            messagesTestCsv.append(("all finished -- db commit finished: time is %s" %(time.ctime(time.time()))))

            return messagesTestCsv
        #//////////                        
#         ## example
#         #select * from cmp, snf where cmp.sl = 242021 and cmp.cmp = 1 and snf.soilkey = 'ABBUFgl###N'
#         sql = "create table %s as select * from %s, %s where %s.%s = %s and %s.%s = %s and %s.%s = '%s'" %(resultsTableName, cmpTableName, snfTableName, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId, snfTableName, dbSoilKey, snfSoilKeyToUse)
# 
#         # create sql insert strings
#         sql = "insert into %s select * from %s, %s where %s.%s = %s and %s.%s = %s and %s.%s = '%s'" %(resultsTableName, cmpTableName, snfTableName, cmpTableName, dbSlcKey, slcId, cmpTableName, dbCmpKey, cmpId, snfTableName, dbSoilKey, snfSoilKeyToUse)
#         sqlInserts.append(sql)
        
        
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
    
    
    # //////////////////// categorical and numeric column calculations
    def calculateField(self, slcIds, dbSlcKey, tableName, columnName, dbPercentKey):
        """
        purpose:
        calculate user selected column. determines field type to dispatch either numeric or categorical calculation
        by slc id.
        
        notes:
        dbSlcKey is column for slc id's.
        slcIds is any iterable object. 
        
        how:
        sql query via python to db
        
        returns:
        sql query headers & results        
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
            elif fieldDataType.lower().startswith("int") or fieldDataType.lower().startswith("rea") or fieldDataType.lower().startswith("flo"):
                columnDataType = "numeric"
                return columnDataType
            else:
                print "could not match data type!!"
            

                
        def categoricalCalculation(slcIds, dbSlcKey, tableName, columnName, dbPercentKey):
            """
            - dominate based on higest sum percent value for unique values. count is not
            a factor in determining.
            - * check if result class = ""; replace with "NULL"
    
            calculates dominate/sub-dominate results for single string db field
    
            returns columns headers plus results.
            """
        
            # hold select dominate/sub-dominate data
            results = []
            
            sqlStatements = []
            
            # default for slc id polygon data type is numeric
            slcIdKeyNumeric = True
            
            # check if slc (polygon) id is alphanumeric ie ONAD405357
            test_value = slcIds[0]
            
            if type(test_value) == str or type(test_value) == unicode:
                slcIdKeyNumeric = False
            
            for slcId in slcIds:
                # process each sl id separatly
            
                # summarize single sl id. determine count of categories present. rank by high-low.
                # dominate has highest count, sub-dominate is second highest.
                
                ## = examples
                ## select sl, dominate_category, dominate_weight from (select distinct(slope) as dominate_category,sl,sum(percent) as dominate_weight from cmp32 where sl = 254001 group by slope order by count(slope) desc limit 1) as  t
                ##sql = """select distinct(%s),count(%s) as count, sum(percent) as dominance from %s where %s = %s group by %s order by count(%s) desc""" %(dbSlcKey,column,column,tableName,dbSlcKey,slcId,column,column)
                
                if slcIdKeyNumeric:
                    # key is numeric. no quoted slc id = value
                    # return 2 rows, first = dominate; second if present if sub-dominate
                    sql = "select %s, dominate_category, dominate_weight, dominate_count, sub_dominate_category, sub_dominate_weight from (select distinct(%s) as dominate_category, %s, sum(%s) as dominate_weight, count(%s) as dominate_count, NULL as sub_dominate_category, NULL as sub_dominate_weight from %s where %s = %s group by %s order by count(%s) desc limit 2) as t " %(dbSlcKey, columnName,dbSlcKey,dbPercentKey,columnName, tableName, dbSlcKey, slcId,columnName,columnName)
                else:
                    # key is alphanumeric. quote sld id = 'value'
                    sql = "select %s, dominate_category, dominate_weight, dominate_count, sub_dominate_category, sub_dominate_weight from (select distinct(%s) as dominate_category, %s, sum(%s) as dominate_weight, count(%s) as dominate_count, NULL as sub_dominate_category, NULL as sub_dominate_weight from %s where %s = '%s' group by %s order by count(%s) desc limit 2) as t " %(dbSlcKey, columnName,dbSlcKey,dbPercentKey,columnName, tableName, dbSlcKey, slcId,columnName,columnName)
                
                # capture sql statement
                sqlStatements.append(sql)
                
            #execute sql
            results = self.executeSql(sqlStatements, fieldNames=True, multipleSqlString=True)
            
            
            #== clean up returned data
            #example: [['sl', 'dominate_category', 'dominate_weight', 'dominate_count', 'sub_dominate_category', 'sub_dominate_weight'], [(251011, u'A', 50, 2, None, None), (251011, u'B', 50, 1, None, None)]]
            
            cleanedResults = []
            
            for e in results:
                # get second item containing data
                rawResults = e[1]
                # check if value present
                if len(rawResults) == 0:
                    # no data
                    pass
                elif len(rawResults) > 1:
                    # have dominate and subdominate. remove sub-dominate slc id number
                    # convert dominate/sub-dominate into sep lists
                    tmpDominate = list(rawResults[0])
                    tmpSubDominate = list(rawResults[1])
                    # remove sub-dominate slc id
                    tmpSubDominate.pop(0)
                    # combine lists together
                    tmpResults = tmpDominate + tmpSubDominate
                    # remove None values
                    # add to cleaned up data. remove None from data
                    cleanedResults.append([a for a in tmpResults if a])
                else:
                    # only dominate present
                    # extract tuple items from list
                    # add to cleaned up data. remove None from data
                    cleanedResults.append([a for l in rawResults for a in l if a])
            
            #== return headers and results
            # prefix header with column name
            headers = results[0][0]
            headerFormat = "%s_%s"
            # remove columnName quoting of '"name"'
            columnName = columnName.strip('"')
            headersPrefixed = [headerFormat%(columnName, x) for x in headers]

            return headersPrefixed, cleanedResults


        def numericCalculation(slcIds, dbSlcKey, tableName, columnName, dbPercentKey):
            """
            purpose:
            calculates weighted summed average of single numeric db field by slc id
            
            how:
            sql query
            
            notes:
            db drops rows with no data
            
            returns:
            sl id and value
            """
            
            # hold calculated sum weighted value
            results = []
            
            sqlStatements = []
            
            # default for slc id polygon data type is numeric
            slcIdKeyNumeric = True
            
            # check if slc (polygon) id is alphanumeric ie ONAD405357
            test_value = slcIds[0]
            
            if type(test_value) == str or type(test_value) == unicode:
                slcIdKeyNumeric = False
            
            for slcId in slcIds:
                # process each sl id separatly
                
                ## = examples
                ## select distinct(sl) as sl, sum(awhc_v * (percent/100.0)) as final from cmp32 where sl = 376002 group by sl
                ## sql = """select distinct(sl) as sl, sum(%s * (percent/100.0)) as final from %s where sl = %s group by sl""" %(column,tableName,sl)
                
                if slcIdKeyNumeric:
                    # key is numeric. no quoted slc id = value
                    sql ="select distinct(%s) as %s, sum(%s * (%s/100.0)) as weighted_average from %s where %s = %s group by %s" % (dbSlcKey, dbSlcKey, columnName, dbPercentKey, tableName, dbSlcKey,  slcId, dbSlcKey)
                else:
                    # key is numeric. quoted slc id = 'value'
                    sql ="select distinct(%s) as %s, sum(%s * (%s/100.0)) as weighted_average from %s where %s = '%s' group by %s" % (dbSlcKey, dbSlcKey, columnName, dbPercentKey, tableName, dbSlcKey,  slcId, dbSlcKey)

                # add sql statement
                sqlStatements.append(sql)
            
            
            #execute sql
            results = self.executeSql(sqlStatements, fieldNames=True, multipleSqlString=True)
            
            #== clean up returned data
            #example: "['sl', 'weighted_average']","[(242022, -3.3000000000000003)]"
            
            cleanedResults = []
            
            for e in results:
                # get second item containing data
                rawResults = e[1]
                # check if value present
                if len(rawResults) == 0:
                    # no data
                    pass
                else:
                    # format calculated value to 2 decimal places
                    formattedNumber = [rawResults[0][0],"{:0.2f}".format(round(rawResults[0][1],2))]
                    # add to cleaned up data. remove None from data
                    cleanedResults.append(formattedNumber)
                        
            # return headers and results. headers will be last iteration.
            #return header, results
            # prefix header with column name
            headers = results[0][0]
            headerFormat = "%s_%s"
            # remove columnName quoting of '"name"'
            columnName = columnName.strip('"')
            headersPrefixed = [headerFormat%(columnName, x) for x in headers]
            
            return headersPrefixed, cleanedResults
        
        
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
            # issue determining column data type
            print "mmmm couldn't figure out column type"
            print columnDataTypeIs

