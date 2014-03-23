"""
purpose:
handles all file input/output and conversions

notes:
-creates spatialite db (sqlite with spatial extenions). 
-the cmp dbf is converted to the spatialite via qgis api. subsequent dbf's are converted to csv via qgis api and loaded into db via python
-output of soil column calculated csv's handled here

license:
gpl3

developer:
richard burcher
richardburcher@gmail.com
2014
"""

import os
import csv
import sqlite3
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


class Io:
    """
    purpose:
    handles all io
    """
    
    def __init__(self, **kwargs):
        # db path
        self.sqliteDbPath = kwargs.get("inSoilDbPath", None)

        # temp system directory
        self.tmpDirectory = kwargs.get("tempSystemDirectoryPath", None)
    

    def createNewDb(self, namesToPaths):
        """
        purpose:
        create spatialite soil db
        
        notes:
        -create initial spatialite db using cmp db; this table is always used
        -names of tables are generic, cmp/snf/slf are used
        
        returns:
        boolean status of db creation and data load
        """
        
        # status of loading layers via qgis api 
        loadStatus = True
        
        def createInitialDb(path, tableName):
            """
            purpose:
            create initial spatialite db by loading cmp soil dbf
            
            how:
            using qgis api to load dbf layer into qgis without showing user. dbf converted to spatialite via ogr
            
            notes:
            cmp table is initially named after the name of db
            
            return:
            nothing
            """

            # loads as qgis vector layer, but do not display on canvas
            # tableName will be table name in spatialite
            dbfLayer = QgsVectorLayer(path,tableName,"ogr")
            
            # check layer valid
            if not dbfLayer.isValid():
                # problem with layer. return issue
                return False
            else:
                # convert cmp dbf to sqlite db
                # write dbf to sqlite. must be spatialite to work for loading back into qgis
                QgsVectorFileWriter.writeAsVectorFormat(dbfLayer,self.sqliteDbPath,"CP1250",None,"SQLite",False,None,["SPATIALITE=yes"])
                
                # loaded ok
                return True


        def addOtherDbfsToDb(path, tableName):
            """
            purpose:
            load additional soil dbf's such as snf, slf into existing spatialite db
            
            how:
            qgis api loads dbf's, converts to csv in tmp location. csv's loaded into existing spatialite db
            
            notes:
            table names are user controlled when loading from csv file
            
            returns:
            nothing
            """

            # tmp path for conversion
            tmpPathToWriteCsv = os.path.join(self.tmpDirectory, tableName)

            # create qgis vector layer
            dbfLayer = QgsVectorLayer(path, tableName,"ogr")
            
            # check if layer valid
            if not dbfLayer.isValid():
                return False
            else:
                # convert to csv using qgis ogr provider
                QgsVectorFileWriter.writeAsVectorFormat(dbfLayer,tmpPathToWriteCsv,"CP1250",None,"CSV",False,None)
    
                # load csv into db.
                self.convert(tmpPathToWriteCsv + ".csv", self.sqliteDbPath,tableName)
                
                return True


        # process cmp dbf first
        # create initial table
        loadStatus = createInitialDb(namesToPaths["cmp"],"cmp")
        
        if loadStatus:
            # remove cmp key from mapping
            namesToPaths.pop("cmp")
        
            # check if additional mapping keys present
            for name, path in namesToPaths.items():
                # process each path
                # convert to csv & load
                loadStatus = addOtherDbfsToDb(path, name)
                
                # check if issues loading additional layers
                if loadStatus:
                    continue
                else:
                    return loadStatus

        else:
            # problem loading layer
            # return load status of layers
            return loadStatus

        return loadStatus

    # ========== read csv file into existing sqlite db
    """
    # A simple Python script to convert csv files to sqlite (with type guessing)
    # https://github.com/rgrp/csv2sqlite/blob/master/csv2sqlite.py
    # @author: Rufus Pollock
    # Placed in the Public Domain\
    """

    def convert(self, filepath_or_fileobj, dbpath, table='data'):
        if isinstance(filepath_or_fileobj, basestring):
            fo = open(filepath_or_fileobj)
        else:
            fo = filepath_or_fileobj
        reader = csv.reader(fo)

        types = self._guess_types(fo)
        fo.seek(0)
        headers = reader.next()

        _columns = ','.join(
            ['"%s" %s' % (header, _type) for (header,_type) in zip(headers, types)]
            )

        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        
        #===== modification to orginial code
        # turn off journaling to speed up csv loading
        c.execute("pragma journal_mode=OFF")
        # set synchronous to normal mode
        c.execute("pragma synchronous=NORMAL")
        # increase page size. default is 1024
        c.execute("pragma page_size=8192")
        # must vacuum for page_size to be used
        c.execute("VACUUM")
        
        
        c.execute('CREATE table %s (%s)' % (table, _columns))

        _insert_tmpl = 'insert into %s values (%s)' % (table,
            ','.join(['?']*len(headers)))
        for row in reader:
            # we need to take out commas from int and floats for sqlite to
            # recognize them properly ...
            row = [ x.replace(',', '') if y in ['real', 'integer'] else x
                    for (x,y) in zip(row, types) ]
            c.execute(_insert_tmpl, row)

        conn.commit()
        c.close()

    def _guess_types(self, fileobj, max_sample_size=100):
        '''Guess column types (as for SQLite) of CSV.

        :param fileobj: read-only file object for a CSV file.
        '''
        reader = csv.reader(fileobj)
        # skip header
        _headers = reader.next()
        # we default to text for each field
        types = ['text'] * len(_headers)
        # order matters
        # (order in form of type you want used in case of tie to be last)
        options = [
            ('text', unicode),
            ('real', float),
            ('integer', int)
            # 'date',
            ]
        # for each column a set of bins for each type counting successful casts
        perresult = {
            'integer': 0,
            'real': 0,
            'text': 0
            }
        results = [ dict(perresult) for x in range(len(_headers)) ]
        for count,row in enumerate(reader):
            for idx,cell in enumerate(row):
                cell = cell.strip()
                # replace ',' with '' to improve cast accuracy for ints and floats
                cell = cell.replace(',', '')
                for key,cast in options:
                    try:
                        # for null cells we can assume success
                        if cell:
                            cast(cell)
                        results[idx][key] += 1
                    except (ValueError), inst:
                        pass
            if count >= max_sample_size:
                break
        for idx,colresult in enumerate(results):
            for _type, dontcare in options:
                if colresult[_type] == count + 1:
                    types[idx] = _type
        return types


    #////////////////////// csv writer

    def writeCsvFile(self, column, headers, data, path, csvFilePrefixName):
        """
        purpose:
        write csv file containing either numeric/categorical calculation results
        
        how:
        python
        
        notes:
        prefix filename with user defined word
        base name of csv is column derived
        
        returns:
        full path to output csv
        """
        
        # file name
        outName = csvFilePrefixName + "_" + column + ".csv"
        
        # remove quoting and colon from filename
        outNameCleaned = outName.replace(":","_")
        outNameCleaned = outNameCleaned.replace('"',"")
        
        # full csv path
        writeCsvFilePath = os.path.join(path, outNameCleaned)
        
        with open(writeCsvFilePath,"wb") as csvfile:
            f_writer = csv.writer(csvfile,delimiter=",")
            # write headers
            f_writer.writerow(headers)
            # write data
            for e in data:
                # data contains 1:n list/tuples
                f_writer.writerow(e)
        
        return writeCsvFilePath
    