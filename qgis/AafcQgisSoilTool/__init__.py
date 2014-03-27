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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load AafcQgisSoilTool class from file AafcQgisSoilTool
    from aafcqgissoiltool import AafcQgisSoilTool
    return AafcQgisSoilTool(iface)
