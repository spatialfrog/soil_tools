***** PLEASE READ THIS FILE PRIOR TO COMMENCING WITH TOOL *****


Please review the Documentation folder for futher guidance.


Virtual Machine:

-admin rights are required to install virtualbox on windows host.
-for security, the network access of virtual machine can be disabled.
-the amount of ram dedicated to the machine will affect performance. if host system has more than 3GB, please dedicate more ram to machine by shutting down virtual machine. in the virtualbox manager right click the virtual machine & select Settings. Click System & alter Base Memory. Press OK & start virtual machine.
-IMPORTANT --- virtual machine has the capacity to expand to 200GB. monitor host harddrive to ensure space is avaiable (200GB does not have to reserved).



Shared Folders between Host & Virtual Machine:

-please refer to Documentation/Installing_Virtual_Machine_and_Shared_Folder.odt to setup a shared folder.
-IMPORTANT --- each login will require a reconnection between the host & virtual machine shared folders. open terminal & type: sudo mount -t vboxsf vboxshare /media/sf_vboxshare



Using the Tools:

-IMPORTANT --- each site must have own GRASS Location. refer to Documentation/using_multi_scale_tools_tutorial.odt. 
-IMPORTANT --- allows check the region settings. ensure resolution & extent is correct. 
-please cd into the /home/xgeng/Gis directory. this will keep file system orginized. the GRASS database is located here.
-create a unique site directory & cd into prior to starting GRASS. each execution of the r.multiscale_aafc.sh tool creates a new folder (name is based on the input raster to tool) containing a series of outputs.
-to start GRASS, at terminal type "grass64".
-type r.preprocessing_aafc.sh or r.multiscale_aafc.sh to run tools.
-NOTE --- r.multiscale_aafc.sh will delete all rasters in mapset per execution. this ensures that results are not mixed from previous runs. please either copy data to another mapset or within tool under Options tab select the export to geotiff option. r.preprocessing_aafc.sh does not delete mapset.
-permanent mapset should only be used for base layers. do not conduct analysis within, change to alternative mapset.



Cruise/Quest:

-installed in /home/xgeng/Stats_Software
-refer to Documentation/starting_cruise_quest_software.odt



Be Aware Of:

-other software components are used for processing. SAGA is a key software. it has been tested with rasters up to 25 million cells. 
-processing time will be considerable depending on the number of cells & outputs requested.
-ensure that geotiffs imported have been cropped to site extents correctly. null cells are usually set transparent when viewed.



Software Installed:

-Ubuntu 10.04 LTS
-GRASS 6.4.2snv july 2011
-R 2.13.2
-QGIS 1.7.1
-SAGA 2.0.7

-automatic updates have been turned off. please do not turn on. this ensures that the tools work correctly & not subject to system upgrade incompatibilities.
-Python 2.6.5



