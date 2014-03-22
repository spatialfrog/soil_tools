# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AafcQgisSoilTool
                                 A QGIS plugin
 Tools allows interaction with Canadian soli databases hosted on Cansis website
                              -------------------
        begin                : 2014-02-05
        copyright            : (C) 2014 by richard burcher
        email                : richardburcher@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
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
from utilities import Utils
import os.path
import sys
import functools


class AafcQgisSoilTool:
    """
    main tool class
    """
    
    def __init__(self, iface):
        """
        set up references
        """
        
        # Save reference to the QGIS interface
        self.iface = iface
        # save ref to canvas
        self.canvas = self.iface.mapCanvas()
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'aafcqgissoiltool_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
 
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        
        # Create the dialog (after translation) and keep reference
        self.dlg = AafcQgisSoilToolDialog()
        
        self.layer = None
        
        self.utils = Utils(iface)
        
        self.helloWorld ="helloWorld"
        

    def initGui(self):
        """
        set up gui actions and icons.
        """
        
        # actions
        #cmpDbfPath = self.dlg.button_cmpDbfPath.clicked.connect(self.utils.getFilePathFromDialog(self.directoryToSearch))
        #self.utils.communicateWithUserInQgis(cmpDbfPath)
        
        # open configuration file for user editing
        self.actionOpenConfig = QAction(QIcon(":/plugins/aafcqgissoiltool/icon.png"),u"Open configuration file", self.iface.mainWindow())
        # method to run when menu icon pressed
        ##self.actionOpenConfig.triggered.connect(functools.partial(self.utils.getFilePath,searchDirectory=self.directoryToSearch))
        self.actionOpenConfig.triggered.connect(self.utils.openConfigurationDialog)
        
        def displayConfInfo():
            dbSoilName = self.utils.dbSoilName
            self.utils.communicateWithUserInQgis(dbSoilName)
        
        
        # execute processing
        self.action_process_dbf = QAction("Process Soil", self.iface.mainWindow())
        self.action_process_dbf.triggered.connect(displayConfInfo)
        
        #self.dlg.getDbfHeaders.clicked.connect(self.utils.retrieveDbfInformation)
        
        # layer selection changed in qgis toc
        #self.iface.currentLayerChanged.connect(self.utils.currentLayerChanged)
        
        
        # add menu items within qgis. user selection triggers action.
        # add plugin name to pre-existing qgis menu location. using plugin menu.
        self.iface.addPluginToMenu(u"&AAFC Soil Tool", self.actionOpenConfig)
        self.iface.addPluginToMenu("&AAFC Soil Tool", self.action_process_dbf)
        

    def unload(self):
        """
        plugin tear down for uninstall
        """
        
        # remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&AAFC Soil Tool", self.action_open_file)
        self.iface.removePluginMenu("&AAFC Soil Tool", self.action_process_dbf)
        
        # deregister qt slots
        #self.utils.iface.currentLayerChanged.disconnect(self.utils.currentLayerChanged)
        
    
    
    
    
    