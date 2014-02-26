#/***************************************************************************
# AafcQgisSoilTool
#
# Tools allows interaction with Canadian soli databases hosted on Cansis website
#                             -------------------
#        begin                : 2014-02-05
#        copyright            : (C) 2014 by richard burcher
#        email                : richardburcher@gmail.com
# ***************************************************************************/
#
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

# EXE
PYUIC=/opt/local/bin/pyuic4-2.7
PYRCC=/opt/local/bin/pyrcc4-2.7

# CONFIGURATION
PLUGIN_UPLOAD = $(CURDIR)/plugin_upload.py

QGISDIR=.qgis2

# Makefile for a PyQGIS plugin

# translation
SOURCES = aafcqgissoiltool.py utilities.py ui_aafcqgissoiltool.py __init__.py aafcqgissoiltooldialog.py
#TRANSLATIONS = i18n/aafcqgissoiltool_en.ts
TRANSLATIONS =

# global

PLUGINNAME = aafcqgissoiltool

PY_FILES = aafcqgissoiltool.py utilities.py aafcqgissoiltooldialog.py __init__.py

EXTRAS = icon.png metadata.txt

UI_FILES = ui_aafcqgissoiltool.py

RESOURCE_FILES = resources_rc.py

HELP = help/build/html

default: deploy

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	$(PYRCC) -o $*_rc.py  $<

%.py : %.ui
	$(PYUIC) -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/$(QGISDIR)/python/plugins
deploy: derase compile
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	#cp -vfr i18n $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	#cp -vfr $(HELP) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
# zip: deploy dclean
#	rm -f $(PLUGINNAME).zip
#	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip.
# This requires use of git (your plugin development directory must be a
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
# package: compile
#		rm -f $(PLUGINNAME).zip
#		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
#		echo "Created package: $(PLUGINNAME).zip"

# upload: zip
#	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

# transup
# update .ts translation files
transup:
	pylupdate4 Makefile

# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

# build documentation with sphinx
doc:
	cd help; make html
