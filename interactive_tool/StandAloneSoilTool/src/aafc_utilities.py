# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:22:00 2014

@author: drownedfrog
"""

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
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
        load single db layer from spatialite into qgis toc as vector layer.
        connection string created to load.

        must provide full path including extension.

        returns message if issue with loading layer.
        """

        ## orginial load
        ##self.iface.addVectorLayer(filename,file_name,provider)

        # parameterize connection string
        connectionUrl = 'dbname=%s table=%s, %s, %s' %(filePath, tableName, tableName, provider)

        # create qgis vector layer. connection url to single db table
        ### QgsVectorLayer('dbname="/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev/data/test/cmp32.sqlite" table="cmp32"', 'cmp32_db', 'spatialite')
        dbTableToLoadAsVectorLayer = QgsVectorLayer(connectionUrl)

        # check if layer is valid
        if dbTableToLoadAsVectorLayer.isValid():
            # register layer to display within qgis
            QgsMapLayerRegistry.instance().addMapLayer(dbTableToLoadAsVectorLayer)
        else:
            return "Issue loading db layer. Check connection url ", connectionUrl


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
        
        #TODO: validate input -- check cmp table passed; check filename. if not warning and quite
        
        cmpDbfPresent = False
        
        # process all passed parameters
        for item in params:
            # is file path
            if os.path.isfile(item):
                # check valid path
                if not os.path.exists(item):
                    return ("invalid path supplied", False)
                
                fileName = os.path.basename(item)
                # check if cmp supplied
                if "cmp" in fileName.lower():
                    cmpDbfPresent = True
            
            # path exits
            if not os.path.exists(item):
                return ("invalid path supplied", False)
            
            else:
                pass
        
        if not cmpDbfPresent:
            # cmp dbf table absent
            return ("cmp dbf missing", False)
        
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
        
        
            
    
    
    
    




