soil tools
==========

multiscale tool
---------------
designed to process elevation data through a varitey of user defined spatial scales. at each scale a series of derivative layers are created for later analysis.

requirements:
-designed for use within a linux system
-grass 6.4.3
-saga 2.1.1
-gdal 1.10
-R 3.0.2. need to install spatial packages spgrass6/raster/xml/rgdal/rsaga/sp

install:
-copy to the grass scripts directory. ensure script permission set to +x

running:
-invoke grass from terminal
-type "r.multiscale_aafc.sh"


qgis
----
series of python scripts to allow processing of Canadian SLC soil databases

requirements:
-windows requires qgis >=2.2
-mac osx was fine with qgis 2.0.1

install:
-copy all files/dirs within /src directory to 'user_name'/.qgis2/processing/scripts

notes:
-must run qgis after install to create the .qgis2 directory

running:
-launch qgis
-on main application menu click Processing -- Toolbox
-located under Scripts/[AAFC Soil Tools]
-can skip "0 create soil db" by using precreated sqlite db found -----TO ADD
