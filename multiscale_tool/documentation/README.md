Overview
========

Designed to process elevation data through a variety of user defined spatial scales. at each scale a series of derivative layers are created for later analysis

Installing
----------

Copy to the grass scripts directory. Ensure the script permission set to +x

### Requirements

Designed for use within a Linux operating system. You will need to install the following:

#### Software

GRASS 6.4.3

SAGA 2.1.1

GDAL 1.10

R 3.0.2. Need to install packages spgrass6/raster/xml/rgdal/rsaga/sp

Running
------- 

Invoke GRASS from the system terminal.

Type "r.multiscale_aafc.sh" to launch.

Workflow
========

#### Important
Unless a common coordinate system is used, different projections will require own GRASS Location.
Always check the region settings. Ensure resolution and extent is correct. 
The script r.multiscale_aafc.sh will delete all rasters in a mapset at beginning of execution. This ensures that results are not mixed from previous runs. Please either copy data to another mapset or within tool under Options tab select the export to geotiff option. .
Permanent mapset should only be used to load in base layers for reference in other mapsets. Do not conduct analysis within, change to alternative mapset.

Create a unique site directory and cd into prior to starting GRASS. Each execution of the r.multiscale_aafc.sh tool creates a new folder (name is based on the input raster to tool) containing a series of outputs.
Start GRASS at terminal by typing "grass64".
Type r.multiscale_aafc.sh to launch tool.

Output
======

GRASS rasters and vector datasets created per run of the script. User must select to export GRASS rasters to GEOTIF format in the Options tab to allow use of data in other data packages. 
