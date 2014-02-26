"""
helper class methods
"""

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from aafcqgissoiltooldialog import AafcQgisSoilToolDialog
import os.path
import sys

class Utils:
    """
    utility class
    """
    
    def __init__(self,iface):
        """
        constructor
        """
        
        self.iface = iface
        
    
    def getFilePath(self,searchDirectory,filter="dBASE (*.dbf)"):
        """
        present standard qt file dialog. user selects single file.
        
        returns full file path.
        """
        
        # TODO: provide enumeration similar to communicateWithUserInQgis for filter type. only permit dbf & shp
        
        # get full path to file
        filepath,filter = QFileDialog.getOpenFileNameAndFilter(self.iface.mainWindow(),"Please choose a file to open...",
                    searchDirectory,filter,"Filter list for selecting files from a dialog box")
        
        if len(filepath) == 0:
            return None
        else:
            self.communicateWithUserInQgis(filepath)
            return filepath
    
    
    def loadVectorLayerQgis(self,filepath,filename="loaded_vector",provider="ogr"):
        """
        load single vector layer into qgis application
        """
        
        # TODO: check valid layer. report via qgis msg log system if not.
        
        self.iface.addVectorLayer(filename,file_name,provider)
    
    
    def communicateWithUserInQgis(self,message,level="INFO",duration=5):
        """
        provides standardized way to communicate with user. qgis message bar
        system is used.
        """
        
        # get reference to qgis message bar
        messageBar = iface.messageBar()
        
        # construct level to output
        if level == "WARNING":
            displayLevel = messageBar.WARNING
        elif level == "CRITICAL":
            displayLevel = messageBar.CRITICAL
        else:
            displayLevel = messageBar.INFO
        
        # output message
        messageBar.pushMessage(message,displayLevel,duration)
        
    
    def retrieveDbfInformation(self,userDefinedId="SL"):
        """
        gets basic information about loaded dbf layer.
        
        returns headers, unique row id numbers as defined by user.   
        """
        
        # headers
        if self.layer == None:
            self.communicateWithUserInQgis("No vector layer selected\n. Must select a layer!", "CRITICAL") 
            return
        # get data provider
        provider = self.layer.dataProvider()
        # dict mapping of key = name, value = index in attribute table
        fields = provider.fieldNameMap()
        
        return fields
        
    
    def currentLayerChanged(self,currentLayer):
        """
        check layer selected in toc. update layer with activeLayer
        """
        
        # no layer selected
        if currentLayer == None: return
        # update layer
        self.layer = self.iface.activeLayer()
        
        QMessageBox.information(self.iface.mainWindow(),"hello",str(self.layer.name()))  

