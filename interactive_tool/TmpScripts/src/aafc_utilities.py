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
        validate all user path inputs. if any path incorrect, return error message
        of first incorrect path
        """

        # simply check all paths correct
        for e in params:
            if os.path.exists(e):
                continue
            else:
                return "Path %s is incorrect. Please check again." % (e)


    def removeAllQgisLayers(self):
        """
        remove all layers in the qgis toc
        """

        # remove all layers in qgis
        QgsMapLayerRegistry.instance().removeAllMapLayers()


    def determineSystemTempDirectory(self):
        """
        return path of system temp directory
        """

        return tempfile.gettempdir()
    
    
    def convertDbResults2SimpleList(self,data):
        """
        convert db query data from list of tuples into simple list
        
        returns list
        """
        
        results = []
        for i in data:
            # extract single value from tuple
            results.append((i[0]))
        
        return results
    




