"""
handles all file input/output and conversions
"""

import os
import csv
import sqlite3
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


class Io:
    """
    handles all io
    """

    def __init__(self, sqliteDbPath, tmpSystemDirectory):
        # db path
        self.sqliteDbPath = sqliteDbPath

        # temp system directory
        self.tmpDirectory = tmpSystemDirectory


    def createNewDb(self, cmpDbfPath, *params):
        """
        create initial spatialite db using cmp db; this table is always used.

        name of table determined from basename of dbf minus extension.

        pass additional dbf's to be added.
        """

        def determineDbfName(dbfPath):
            """
            return basename of dbf minus extension
            """

            return os.path.splitext(os.path.basename(dbfPath))[0]


        def createInitialDb(cmpDbfPath, tableName):
            """
            create initial spatialite db
            """

            # TODO: error checking and reporting -- loading cmp dbf

            # loads as qgis vector layer, but do not display on canvas
            # tableName will be table name in spatialite
            dbfLayer = QgsVectorLayer(cmpDbfPath,tableName,"ogr")

            # convert cmp dbf to sqlite db
            # write dbf to sqlite. must be spatialite to work for loading back into qgis
            QgsVectorFileWriter.writeAsVectorFormat(dbfLayer,self.sqliteDbPath,"CP1250",None,"SQLite",False,None,["SPATIALITE=yes"])


        def addOtherDbfsToDb(dbfPath, tableName):
            """
            add snl/snf or other dfb's to spatialite db.

            convert to csv and then import.
            """

            # TODO: error checking -- loading additional tables

            # temp path for conversion
            tmpPathToWriteCsv = os.path.join(self.tmpDirectory, tableName)

            # create qgis vector layer
            dbfLayer = QgsVectorLayer(dbfPath, tableName,"ogr")

            # convert to csv using qgis ogr provider
            QgsVectorFileWriter.writeAsVectorFormat(dbfLayer,tmpPathToWriteCsv,"CP1250",None,"CSV",False,None)

            # load csv into db.
            self.convert(tmpPathToWriteCsv, self.sqliteDbPath,tableName)


        # process cmp dbf first
        tableName = determineDbfName(cmpDbfPath)
        # create initial table
        createInitialDb(cmpDbfPath,tableName)

        #TODO: parse additional *params and load dbf's into db


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

    # ===========

    def writeCsvFile(self, headers, data,path):
        """
        TODO: write db processing results to csv
        """

        pass
