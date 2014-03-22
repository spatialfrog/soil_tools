# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:22:00 2014

@author: drownedfrog
"""

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
# qgis processing framework
import processing

import os
import tempfile



class Utils:
    """
    utility class
    """

    def __init__(self,iface):
        """
        constructor
        """

        self.iface = iface


    def loadDbTableAsLayerIntoQgis(self, filePath, tableName, provider="spatialite"):
        """
        purpose:
        load single db layer from spatialite into qgis toc as vector layer
        
        notes:
        must provide full path including extension
        
        returns:
        tuple containing (msg, boolean status)
        """

        # parameterize connection string
        connectionUrl = 'dbname=%s table=%s' %(filePath, tableName)

        # create qgis vector layer. connection url to single db table
        ### QgsVectorLayer('dbname="/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/cmp32.sqlite" table="cmp32"', 'cmp32_db', 'spatialite')
        dbTableToLoadAsVectorLayer = QgsVectorLayer(connectionUrl, tableName, provider)

        # check if layer is valid
        if dbTableToLoadAsVectorLayer.isValid():
            # register layer to display within qgis
            QgsMapLayerRegistry.instance().addMapLayer(dbTableToLoadAsVectorLayer)
            return ("Successfully loaded", True)
        else:
            msg = "Issue loading db layer. Check connection url ", connectionUrl
            return (msg, False)
    
    
    def removeLayerFromQgis(self, layerName):
        """
        purpose:
        remove layer from qgis
        
        how:
        get list of layers from qgis, search for user providers name in layers and then remove
        
        returns:
        nothing
        """
        
        # get listing of layers in qgis
        mapLayerRegistry = QgsMapLayerRegistry.instance()
        layersPresent = mapLayerRegistry.mapLayers()
        
        # check for user supplied name being in qgis layers
        for layer in layersPresent.keys():
            if layerName in layer:
                # found match. remove layer
                mapLayerRegistry.removeMapLayer(layer)
        
        
    def loadVectorLayerIntoQgis(self, filePath, provider="ogr"):
        """
        purpose:
        load vector layer into qgis
        
        how:
        uses qgis api
        loaded layer name in qgis toc is filename minus extension
        
        notes:
        default provider is ogr
        
        returns:
        tuple containing (msg, boolean status)
        """
        
        # name provider for loaded vector in qgis toc. just filename minus extension
        layerName = os.path.splitext(os.path.basename(filePath))[0]
        
        # load vector layer
        addedVector = QgsVectorLayer(filePath, layerName, provider)
        
        # check if valid layer
        if addedVector.isValid():
            # valid qgis vector layer
            # register layer to display within qgis
            QgsMapLayerRegistry.instance().addMapLayer(addedVector)
            return ("Successfully loaded", True)
        else:
            msg = "Issue loading vector layer. Check valid vector layer ", filePath
            return (msg, False)
    

    def communicateWithUserInQgis(self, message,level="INFO", messageExistanceDuration=5):
        """
        provides standardized way to communicate with user. qgis message bar
        system is used.

        user passes string to be displayed.
        level refers to severity of message. 3 choices: WARNING/CRITICAL/INFO.
        messageExistanceDuration is number of seconds qgis message bar is displayed.
        """

        # get reference to qgis message bar
        messageBar = iface.messageBar()
        
        # clear any previous message
        messageBar.clearWidgets()

        # construct level to output
        if level == "WARNING":
            displayLevel = messageBar.WARNING
        elif level == "CRITICAL":
            displayLevel = messageBar.CRITICAL
        elif level == "INFO":
            displayLevel = messageBar.INFO
        else:
            displayLevel = messageBar.INFO

        # output message to qgis
        messageBar.pushMessage(message, displayLevel, messageExistanceDuration)


    def cleanUp(self, dbConnection):
        """
        house cleaning prior to script ending.
        """

        dbConnection.close()


    def checkFileExits(self, path):
        """
        check path exists for full given path. return True/False.
        """

        if os.path.exists(path):
            return True
        else:
            return False


    def deleteFile(self, path):
        """
        checks path exists, then deletes.
        """

        if os.path.exists(path):
            # remove file
            os.remove(path)


    def validateUserInput(self, *params):
        """
        purpose:
        validate user inputs. primialarly concerned with file/directory path correct.
        
        how:
        check each item passed
        
        returns
        tuple consisting of message and status of True/False
        """
        
        #TODO: validate -- input further from config file
        
        # only chek what is passed
        # check type of table join required; this will drive everything thing else. must have certain fields if 2 table join
        # extension dbf present in paths
        # values present for keys required
        # no odd characters in filenames
        # pass back first error and we stop in return code
        #?? sub methods for each type of table config?
        
        cmpDbfPresent = False
        
        # process all passed parameters
        for item in params:
            # do not process blank entries ie qgis processing framework optional value provides ""
            if item =="":
                continue
            # do not process None
            if item == None:
                continue
            # is file path
            if os.path.isfile(item):
                # check valid path
                if not os.path.exists(item):
                    msg = "invalid file path supplied for: %s" %(item)
                    return (msg, False)
                
                fileName = os.path.basename(item)
                # check if cmp is in filename
                if "cmp" in fileName.lower():
                    cmpDbfPresent = True
                
            # directory path exits
            if os.path.exists(item):
                continue
            else:
                msg = "invalid directory path for: %s" %(item)
                return (msg, False)
        
        if not cmpDbfPresent:
            # cmp dbf table absent
            return ("cmp dbf path incorrect", False)
        
        return ("user input ok", True)


    def determineSystemTempDirectory(self):
        """
        return path of system temp directory
        """

        return tempfile.gettempdir()
        
    
    def getTableNamesToPathFromDbfPaths(self, *params):
        """
        purpose:
        parse table names from user supplied dbf file paths. it is expected
        that path will contain cmp/slf/snf in filename. * these become the
        table names in db.
        
        how:
        simple string match against cmp/snf/slf
        
        returns:
        mapping of cmp/slf/snf to dbf path for each if present
        """   
        
        # soil names that must be contained somewhere in file name
        soilNames = ["cmp","snf","slf"]
        
        # mapping of found soil names to full dbf path
        nameToFilePath = {}
        
        for soilName in soilNames:
            # process supplied file paths
            for path in params:
                # skip None
                if path == None:
                    continue
                # get file name
                fileName = os.path.basename(path)
                if soilName in fileName.lower():
                    # match found
                    nameToFilePath[soilName] = path
        
        return nameToFilePath
    
    
    def getTableProcessingOptions(self, soilTableNames):
        """
        purpose:
        provide user options for use of soil tables
        
        notes:
        - cmp  --> default and min
        - cmp - snf
        - cmp - snf - slf
        
        how:
        check listing of soil tables. then construct listing. cmp is base table for everything.
        
        returns:
        mapping of table join options. key is numeric while value is string of table ordering
        ie 0:cmp
        """
        
        tableOptions = {}
        
        for name in soilTableNames:
            if "cmp" in name.lower():
                tableOptions[0] = "cmp"
                continue
            elif "snf" in name.lower():
                tableOptions[1] = "cmp - snf"
                continue
            elif "slf" in name.lower():
                tableOptions[2] = "cmp - snf - slf"
        
        return tableOptions
    
    
    def getQgisTableLayerFilePathInfo(self, tableName, pathKey="dbname"):
        """
        purpose:
        return user requested file path connection details based on key provided
        
        notes:
        returns value based on user supplied key
        key is either "dbname" or "table"
        
        returns:
        string
        """
        
        # convert attribute name to qgis object using processing convience method
        inputLayer = processing.getObject(tableName)

        # get qgis data provider for layer
        provider = inputLayer.dataProvider()
        # get full url connection path ie dbname="some/file/db.sqlite table=some_table"
        url = provider.dataSourceUri()
        # split on space 
        dbFilePath = url.split(" ")
        
        if pathKey == "dbname":
            # second split on '='
            dbFilePath = dbFilePath[0]
            # connection path
            # get db file path
            dbFilePath = dbFilePath.split("=")[1]
            return dbFilePath
        else:
            # second split on '='
            dbFilePath = dbFilePath[1]
            # connection path
            # get db table name
            dbFilePath = dbFilePath.split("=")[1]
            return dbFilePath
    
    
    def getVectorLayerFieldValues(self,vectorLayer, fieldName):
        """
        purpose:
        return all field values for vector layer using qgis processing conveince function
        
        notes:
        takes into account feature selection
        
        returns:
        tuple of (message, list of values, boolean status)
        """
        
        # convert attribute name to qgis object using processing convience method
        inputLayer = processing.getObject(vectorLayer)
        
        # get field values
        fieldValues = processing.values(inputLayer, fieldName)
        
        # convert from dict to list
        values = fieldValues[fieldName]
        
        # check values present
        if len(values) == 0:
            return ("no values for vector layer fieldname provided", None, False)
        else:
            return ("values present", values, True)
        
    