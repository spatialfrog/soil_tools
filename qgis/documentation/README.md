Overview
========

A series of Python scripts within QGIS to process the Canadian SLC soil DBF databases

QGIS provides the GUI front-end through the Processing Framework and its Python API. These provide the ability to load, interact and calculate the SLC soil data.

All scripts are written using Python 2.7 and its standard modules. Installing QGIS provides the standalone Python installation required. 

The SLC DBF databases are loaded into a single SQLite database. A separate table is created per DBF and generically named after the DBF ie cmp, snf or slf. The loaded DBF's must contain the word cmp, slf or snf in the filename. The CMP DBF is manditory to load. SQLite provides a complete RDBMS platform with full SQL support. It is a single file, administrator less RDBMS that allows sharing the single file. Using SQL, the loaded tables can be queried, calculated or joined as the business logic requires. We take take advantage of QGIS to provide initial conversion of the CMP DBF soil database to SQLite and load any remaining DBF's into the new database via Python.

Installing
----------

### Requirements
QGIS >= 2.2 on Windows

QGIS >= 2.0.1 on Mac OSX

### Notes
Must run QGIS after installing to create the .qgis2 directory

### Installing Scripts
Copy all files and directories within the /src directory to 'user_name'/.qgis2/processing/scripts

Running
-------

Launch QGIS, on the main application menu click Processing -- Toolbox.
The scripts are located under Scripts/[AAFC Soil Tools]

Data
====

https://www.dropbox.com/sh/rmpkzw6c3n6vgz3/tRWNJ5a_3U

This provides a complete SQLite soil database with the Canadian SLC CMP, SNF and SLF DBF's loaded. SLC polygon shapefiles for Alberta and PEI are provided.

Help
====

Each script contains self describing documentation

Run the script and select "Help" tab.

Workflow
========

Scripts are numbered numerically to indicate the workflow progression that the user will take

### 0 create soil db
Is only required if a new soil database needs to be created on the file system. Once a database is created it can be reused. Spatial selection is not taken into account when loading data.

### 1 connect soil db 
Is mandatory for any new QGIS session, as it loads all database table data, this includes the CMP soil table, any previous joined tables and if the SNF and/or SLF DBF's were loaded into the initial database a tabled called ���possibleJoinsToCreate��� for the user. It also loads the polygon SLC shapefile selected by the user.

### 2 calculate cmp soil table column 
Provides a single interaction point for the CMP soil table. The user specifies what field in the CMP table to calculate the dominate/sub-dominate or numerical weighted average by SLC id depending on the column datatype. Spatial selection of the SLC polygons are considered, meaning if only five polygons where selected before running the tool then only five SLC polygons will be processed. No spatial selection means that all polygon SLC's will be processed. The resultant column calculation is written to disk as a CSV file and added to QGIS as a layer with which to interact with. 

### 3-0 create multi table soil join
Allows the user to create a dynamically produced flat join table between the CMP-SNF or CMP-SNF-SLF soil tables. The SNF or SLF DBF's must have been loaded into the initially created database. The loaded table ���possibleJoinsToCreate��� allows the user to specify what table join type they desire. Spatial selection is accounted for in the join. Depending on the number of features and type of join,  it can take several minutes or longer to complete. For the CMP-SNF the user can only specify what Land-use type they desire in the SNF table; A or N with the default being N. For the CMP_SNF-SLF join, the user specifies SNF Land-use desired and in the SLF table it is the Layer number desired. Regardless of join type, there is only a single row returned per unique SLC id from the CMP table. The joined table is loaded in QGIS named ���joinedSoilTables���.
Joins between soil tables occur on the column that defines a common soilkey or soilmap in each table.

### 3-1 calculate multi table soil join column
Is similar to script '2 calculate cmp soil table column' but used to calculate the single column on the "joinedSoilTable" output from script '3-0 create multi table soil join'.

### 4 calculate all table columns
Is provided as a convenience to calculate every column in the user selected soil table. Again, spatial selection is taken into account for processing. Resultant CSV's are not loaded into QGIS, as this may result in an overwhelming number of layers in the Table of Contents.

Soil Column Calculations
========================

Calculates either the categorical dominate/sub-dominate or numerical weighted average per SLC id

Datatype of the column determines what calculation is called.

### Categorical
Dominate is defined as the largest count of a single category within the SLC id rows. If no dominate, then assignment is purely arbitrary. Sub-dominate is the next highest count.

### Numerical
Weighted summed average for the rows involved per SLC id. A column defined as percent in the cmp table is used for the weighting. Row column value = 9 and row column percent = 20; calculation is (9 * 0.20) + other rows involved.    

Scripts "2 calculate cmp soil table column", "3-1 calculate multi table soil join column" and "4 calculate all table columns" 

Output
======

CSV file per soil column

All CSV's contain the SLC id used, allowing a join between the loaded CSV and SLC polygon shapefile. The CSV headers have the calculated column name prefixed. This avoids calculated column output name collisions if multiple CSV's where to be joined.
