soil tools
==========

multiscale tool
---------------
designed to process elevation data through a varitey of user defined spatial scales. at each scale a series of derivative layers are created for later analysis.

requirements:
<br />
designed for use within a linux system
<br />
grass 6.4.3
<br />
saga 2.1.1
<br />
gdal 1.10
<br />
R 3.0.2. need to install spatial packages spgrass6/raster/xml/rgdal/rsaga/sp

install:
<br />
copy to the grass scripts directory. ensure script permission set to +x

running:
<br />
invoke grass from terminal
<br />
type "r.multiscale_aafc.sh"


qgis
----
series of python scripts to allow processing of Canadian SLC soil databases

requirements:
<br />
windows requires qgis >=2.2
<br />
mac osx was fine with qgis 2.0.1

install:
<br />
copy all files/dirs within /src directory to 'user_name'/.qgis2/processing/scripts

notes:
<br />
must run qgis after install to create the .qgis2 directory

running:
<br />
launch qgis
<br />
on main application menu click Processing -- Toolbox
<br />
located under Scripts/[AAFC Soil Tools]
<br />
can skip "0 create soil db" by using precreated sqlite db found -----TO ADD
