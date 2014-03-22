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
import functools

class Utils:
    """
    utility class
    """
    
    def __init__(self,iface):
        """
        constructor
        """
        
        self.iface = iface
        self.searchPath = "/Users/drownedfrog/Projects/Contracts/AAFC/dec2013_mar2014_tool_dev"
        self.filter = "dBase (*.dbf)"
        self.cmpDbfPath = ""
        self.snfDbfPath = ""
        self.slfDbfPath = ""
        self.dbSoilName = ""
    
    
    def getFilePathFromDialog(self):
        """
        purpose:
        allow user to select file from computer for use in script
        
        how:
        pyqt4
        
        notes:
        filter is used by script to modify what user may search for
        
        returns:
        full path to file
        """
        
        # get full path to file
        filepath = QFileDialog.getOpenFileNameAndFilter(self.iface.mainWindow(),"Please choose a file to open...", self.searchPath, self.filter)

        if not len(filepath) == 0:
            # QFileDialog returns tuple of path, filter used
            # only need file path
            return filepath[0]
            #self.communicateWithUserInQgis(filepath[0])
        else:
            return None

    
    
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
        
    
    def retrieveConfigInformation(self):
        """
        repotr   
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
    
    
    def getCmpDbfPath(self):
        """
        purpose:
        get cmp dbf path from user
        
        returns:
        path
        """
        
        # get dbf path from file dialog
        self.cmpDbfPath = self.getFilePathFromDialog()
        self.dlg.lineEdit_cmpDbfPath.setText(self.cmpDbfPath)
        
    
    def getSnfDbfPath(self):
        """
        purpose:
        get snf dbf path from user
        
        returns:
        path
        """
        
        # get dbf path from file dialog
        self.snfDbfPath = self.getFilePathFromDialog()
        self.dlg.lineEdit_snfDbfPath.setText(self.snfDbfPath)
        
    
    def getSlfDbfPath(self):
        """
        purpose:
        get slf dbf path from user
        
        returns:
        path
        """
        
        # get dbf path from file dialog
        self.slfDbfPath = self.getFilePathFromDialog()
        self.dlg.lineEdit_slfDbfPath.setText(self.slfDbfPath) 
    
    
    def updateConfigDialog(self):
        """
        purpose:
        update config file dialog with values
        
        returns:
        nothing
        """
        
        pass
        
        # update dbf paths
        
    
    def openConfigurationDialog(self):
        """
        open configuration dialog for editing
        """
        
        # Create the dialog (after translation) and keep reference
        self.dlg = AafcQgisSoilToolDialog()
        # show dialog
        self.dlg.show()
        
        # get text value
        self.dbSoilName = self.dlg.lineEdit_sqliteDbName.text()
        
        # get cmp dbf path
        self.dlg.button_cmpDbfPath.clicked.connect(self.getCmpDbfPath)
        
        # get snf dbf path
        self.dlg.button_snfDbfPath.clicked.connect(self.getSnfDbfPath)
        
        # get slf dbf path
        self.dlg.button_slfDbfPath.clicked.connect(self.getSlfDbfPath)
        
        
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass
