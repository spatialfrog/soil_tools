#!/bin/sh

############################################################################
#
# MODULE:       r.preprocessing
# AUTHOR(S):    richard burcher. summer 2011. aafc cansis contract. richardburcher@gmail.com
# PURPOSE:      
# COPYRIGHT:    (C) 2009 GRASS Development Team/richard
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
############################################################################

#%Module
#% description: Preprocessing functionality prior to running r.multiscale_aafc.sh tool
#% keywords: raster,preprocessing
#%End

## -------------------------------- mask creation -----------------------------
#%Option
#% key: mask_input
#% type: string
#% required: no
#% multiple: yes
#% description: Create Mask to exclude areas from calculations. Multiple Rasters accepted. Input must contain values 1 and 0. Output named 'mask_user'.  
#% gisprompt: old,cell,raster
#% guisection: Mask_Creation
#%End

## --------------------------------- dem avg various sources -----------------------------

#%Option
#% key: dem_avg_ref_pts
#% type: string
#% required: no
#% multiple: no
#% description: Reference Vector Points for RMSE.
#% gisprompt: old,vector,vector
#% guisection: Dem_Averaging
#%End

#%Option
#% key: dem_avg_raster1
#% type: string
#% required: no
#% multiple: no
#% description: Input Raster 1. Raster used to set the "region".
#% gisprompt: old,cell,raster
#% guisection: Dem_Averaging
#%End

#%Option
#% key: dem_avg_raster2
#% type: string
#% required: no
#% multiple: no
#% description: Input Raster 2. Final output raster "Weighted_Avg_DEM".
#% gisprompt: old,cell,raster
#% guisection: Dem_Averaging
#%End

## ---------------------------------- Removal of objects & interp w/random pts & rst  ------------------------------------------------
#%Option
#% key: removal_elevation
#% type: string
#% required: no
#% multiple: no
#% description: Input Elevation
#% gisprompt: old,cell,raster
#% guisection: Removal_Rnd_RST_Interp
#%End

#%Option
#% key: random_pts
#% type: double
#% required: no
#% multiple: no
#% answer: 25.0
#% description: Percentage of Points to Randomly Sample for RST Interp. Do not append %.
#% guisection: Removal_Rnd_RST_Interp
#%End

#%Option
#% key: removal_rst_tension
#% type: double
#% description: Spline Tension Parameter.
#% answer: 40
#% guisection: Removal_Rnd_RST_Interp
#%End

#%Option
#% key: removal_rst_smooth
#% type: double
#% description: Spline Smoothing Parameter
#% answer: 0.1
#% guisection: Removal_Rnd_RST_Interp
#%End

##------------------------------------ optional -----------------------------

#%Option
#% key: water_mask
#% type: string
#% required: no
#% multiple: no
#% description: Raster Mask (Only process area within mask).
#% gisprompt: old,cell,raster
#%End

#%Flag
#% key: p
#% answer: 0
#% description: Apply Pre Calc Multi-direction Lee Filter
#%End

#%Flag
#% key: f
#% answer: 0
#% description: Apply Post Calc Multi-direction Lee Filter
#%End

#%Flag
#% key: i
#% description: Invert Raster Mask: (Only process area outside of mask. Excludes area within mask).
#%End

#%Option
#% key: sinkFill_min_slope
#% type: double
#% description: SAGA Fill Sinks XXL Minumum Slope (degree).
#% answer: 0.1
#%End

##============================================================================

if [ -z "$GISBASE" ] ; then
    echo "You must be in GRASS GIS to run this program." 1>&2
    exit 1
fi

if [ "$1" != "@ARGS_PARSED@" ] ; then
    exec g.parser "$0" "$@"
fi


##set GRASS var
#overwrite
g.gisenv set=OVERWRITE=1


## ============================================================================

## apply water mask if avail
if [ $GIS_FLAG_I = 1 -a "$GIS_OPT_WATER_MASK" != "" ]; then
	## invert the raster mask. raster supplied is not processed. ie) hydrology areas, buildings etc
	echo "inverted mask applied to all raster operations"
	r.mask -i $GIS_OPT_WATER_MASK
elif [ "$GIS_OPT_WATER_MASK" != "" ]; then
	##set supplied mask for all raster operations
	echo "mask applied to all raster operations"	
	r.mask $GIS_OPT_WATER_MASK

	echo "water mask applied is: $GIS_OPT_WATER_MASK"
fi



## ============================================================================

#### mask creation
## categorial based for moment. input must contain 0 & 1 values i.e r.mapcalc out=level>2 would give "out" values of 1 & 0.
## combines multiple selected rasters to form mask area. output name is "mask_user"
if [ $GIS_OPT_MASK_INPUT ]; then
	##set region to input rasters
	g.region rast=$GIS_OPT_MASK_INPUT -p
	echo $GIS_OPT_MASK_INPUT
	#r.mapcalc "mask_user=`echo $GIS_OPT_MASK_INPUT | sed -s s/,/+/g`"
	r.patch -z input=$GIS_OPT_MASK_INPUT output=mask_user --overwrite
	##set 0 values to null
	r.null map=mask_user setnull=0
	echo "created mask is 'mask_user'"
fi

## ============================================================================

## dem creation by averaging dem's from multiple sources using ref to determine weighting

## ref input should be 2x greater accuracy.
## random pts generated & extraction of z from 3 inputs. passed to R for calc of RMSE using ref dataset. Weights
## generated & used in GRASS for merging rasters.

## ref: Geomorphometry Concepts, Software, Applications. Hengl,Reuter pg 110-111.
##
## NOTE: input raster names must be less than 10 char or name truncated when adding col to randon_pts
##
if [ $GIS_OPT_DEM_AVG_REF_PTS ]; then
	
	VECTOR_REF=`echo $GIS_OPT_DEM_AVG_REF_PTS | sed s/@.*//`
	RASTER_AVG1=`echo $GIS_OPT_DEM_AVG_RASTER1 | sed s/@.*//`
	RASTER_AVG2=`echo $GIS_OPT_DEM_AVG_RASTER2 | sed s/@.*//`	

	echo $VECTOR_REF $RASTER_AVG1 $RASTER_AVG2

	##region set using the first input raster
	g.region rast=$GIS_OPT_DEM_AVG_RASTER1 -p

	##-----------------------------------------------------------------
	## determine data type to export for filling & filtering if specified

	for e in $RASTER_AVG1 $RASTER_AVG2
	do		
		TYPE_RASTER=`r.info -t $e | awk -F"=" '{print $2}'`
		if [ "$TYPE_RASTER" = "CELL" ]; then
			TYPE=Int16
		else
			TYPE=Float32
		fi
	
		## fill raster using SAGA Fill Sinks XXL (Wang & Liu)
		echo "filling sinks"
		r.out.gdal input=$e format=SAGA type=$TYPE output=saga_export.sdat nodata=-9999	
		saga_cmd libta_preprocessor 5 -ELEV:saga_export.sgrd -FILLED:filled.sgrd -MINSLOPE:$GIS_OPT_SINKFILL_MIN_SLOPE

		## apply saga multi-direction lee filter if selected for post filtering
		if [ $GIS_FLAG_P = 1 ]; then
		 	echo "pre gaussian filter"
			##multi-directional filter
			saga_cmd libgrid_filter 3 -INPUT:filled.sgrd -RESULT:filled_filtered.sgrd -NOISE_ABS:1.0 -NOISE_REL:1.0 -WEIGHTED -METHOD:2

			#import filtered to GRASS
			r.in.gdal -o input=filled_filtered.sdat output=${e}_saga_pre --overwrite
		else
			#import filtered to GRASS
			r.in.gdal -o input=filled.sdat output=${e}_saga_pre --overwrite
		fi  
	done	

	##----------------------------------------------------------------

	
	#set region for conflation correction. input raster1 set as ref, raster2 aligned to this
	echo "setting new region using: ${RASTER_AVG1}_saga_pre"
	g.region rast=$RASTER_AVG1_saga_pre -p
	#copy raster2, set extents to region
	#RASTER2_ALIGN=${RASTER_AVG2}_aligned
	#echo "raster2_align equals: 
	echo "raster2 align is: ${RASTER_AVG2}_saga_pre"
	r.mapcalc "${RASTER_AVG2}_Align_saga_pre = ${RASTER_AVG2}_saga_pre"
	#RASTER2_ALIGN=`echo $RASTER2_ALIGN | sed s/@.*//`
	
	## remove cols raster1 & raster2 if present on ref vector input
	v.db.dropcol map=$GIS_OPT_DEM_AVG_REF_PTS column="raster1"
	v.db.dropcol map=$GIS_OPT_DEM_AVG_REF_PTS column="raster2"


	## modify input rnd vect pts. add 2 additional columns for raster1/2 elevation values
	v.db.addcol map=$GIS_OPT_DEM_AVG_REF_PTS columns="raster1 DOUBLE,raster2 DOUBLE"

	#extract elevation from input rasters
	v.what.rast vector=$GIS_OPT_DEM_AVG_REF_PTS raster=${RASTER_AVG1}_saga_pre column=raster1
	v.what.rast vector=$GIS_OPT_DEM_AVG_REF_PTS raster=${RASTER_AVG2}_Align_saga_pre column=raster2
	

	## R portion to calc RMSE --------------------------
		
	## output file "rasters.rmse.txt" contains rmse calc: col1=raster1, col2=raster2 & col3=weighted_rmse
	
	# ---> current dir not explicity set for output of final txt
	
	rCommands="library(spgrass6)\nx <- readVECT6('"$GIS_OPT_DEM_AVG_REF_PTS"')\n#remove na values from z columns\nx <-na.omit(x@data)\n#rmse function. na.rm=T removes na values\nrmse <-function(obs,pred) sqrt(mean((obs-pred)^2,na.rm=T))\nraster1.rmse <- rmse(x\$elevation,x\$raster1)\nraster2.rmse <- rmse(x\$elevation,x\$raster2)\nweight <-function(rmse) (1/rmse)^2\nraster1.weight <- weight(raster1.rmse)\nraster2.weight <- weight(raster2.rmse)\nsum.weights <-raster1.weight+raster2.weight\n#output to txt file\nfo <-file("'"rasters_rmse.txt"'","'"w"'")\ncat(raster1.weight,raster2.weight,sum.weights,file=fo,sep="'","'")\nclose(fo)"

##orginial R code
##rCommands="library(spgrass6)\n#read in meta & random pts\n#G <-gmeta6()\nx.has.na <- readVECT6('"$GIS_OPT_DEM_AVG_REF_PTS"')\nx.has.na\n#remove na values from z columns\n#x <-x.has.na[ -which(is.na(x.has.na@data$"$VECTOR_REF")),]\n#rmse function. na.rm=T removes na values\nrmse <-function(obs,pred) sqrt(mean((obs-pred)^2,na.rm=T))\nraster1.rmse <- rmse(x.has.na$"$VECTOR_REF",x.has.na$"$RASTER_AVG1")\nraster2.rmse <- rmse(x.has.na$"$VECTOR_REF",x.has.na$"$RASTER_AVG2")\nweight <-function(rmse) (1/rmse)^2\nraster1.weight <- weight(raster1.rmse)\nraster2.weight <- weight(raster2.rmse)\nsum.weights <-raster1.weight+raster2.weight\n#output to txt file\nfo <-file("'"rasters_rmse.txt"'","'"w"'")\ncat(raster1.weight,raster2.weight,sum.weights,file=fo,sep="'","'")\nclose(fo)"


	echo $rCommands | R --vanilla

	#set vars for rmse values -- note that rmse values here have been calc as  w=(1/rmse)^2
	raster1_rmse=`cat rasters_rmse.txt | awk -F"," '{ print $1 }'`
	raster2_rmse=`cat rasters_rmse.txt | awk -F"," '{ print $2 }'`
	sum_weights=`cat rasters_rmse.txt | awk -F"," '{ print $3 }'`

	##equation
	#temp srtm/gdem weighted rasters
	r.mapcalc "raster1=$raster1_rmse * ${RASTER_AVG1}_saga_pre"
	r.mapcalc "raster2_a=$raster2_rmse * ${RASTER_AVG2}_Align_saga_pre" ##aligned raster2 to base of raster 1 (conflation)
	#sum srtm/gdem weighted rasters
	r.mapcalc "raster1_raster2_sum=raster1+raster2_a"

	#output avg raster
	r.mapcalc "Weighted_Avg_DEM=raster1_raster2_sum/$sum_weights"


	##apply post saga mulit-directional lee filter if selected
	
	##----------------------------------------------------------------
	## apply saga gaussian post filtering
	if [ $GIS_FLAG_F = 1 ]; then
		echo "post lee filter"
		
		## determine data type
		TYPE_RASTER=`r.info -t Weighted_Avg_DEM | awk -F"=" '{print $2}'`
		if [ "$TYPE_RASTER" = "CELL" ]; then
			TYPE=Int16
		else
			TYPE=Float32
		fi
		
		r.out.gdal input=Weighted_Avg_DEM format=SAGA type=$TYPE output=saga_export.sdat nodata=-9999	

		##multi-directional filter
		saga_cmd libgrid_filter 3 -INPUT:saga_export.sgrd -RESULT:filtered.sgrd -NOISE_ABS:1.0 -NOISE_REL:1.0 -WEIGHTED -METHOD:2

		#import filtered to GRASS
		r.in.gdal -o input=filtered.sdat output=Weighted_Avg_DEM_post_filtered_lee --overwrite 
	fi	

	##----------------------------------------------------------------


fi


## ============================================================================

## reduction of noise in high res data. focus here on lidar. random pt sample & interp using rst
##
## org input data filled & opt filtered w/multi-dir lee before r.random selects % of pts from dataset. pts interp with v.surf.rst using -t option.
## tension default & not optimized. option to post filter data w/multi-dir lee.
## selection of 25% pts produces acceptable results but work needs to be undertaken to account for rapid infection changes (eg streams).

if [ $GIS_OPT_REMOVAL_ELEVATION ]; then
	echo "starting random pt sample & interp using rst"

	## set GRASS environmental vars
	#set region & res
	RESOLUTION=`r.info -s $GIS_OPT_REMOVAL_ELEVATION | grep nsres | awk -F"=" '{print $2}'`
	g.region -ap rast=$GIS_OPT_REMOVAL_ELEVATION res=$RESOLUTION

	## set mask is applicable
	#if [ $GIS_OPT_MASK !="" ]; then
	#	## remove current mask
	#	#r.mask -r
	#	## set user mask
	#	r.mask -oi input=$GIS_OPT_REMOVAL_MASK
	#fi

	echo "raster is $GIS_OPT_removal_ELEVATION"
	ELEV_RASTER=`echo $GIS_OPT_REMOVAL_ELEVATION | sed s/@.*//`


	## determine data type
	TYPE_RASTER=`r.info -t $ELEV_RASTER | awk -F"=" '{print $2}'`
	if [ "$TYPE_RASTER" = "CELL" ]; then
		TYPE=Int16
	else
		TYPE=Float32
	fi
		 
	## fill raster using SAGA Fill Sinks XXL (Wang & Liu)
	echo "filling sinks"
	r.out.gdal input=$ELEV_RASTER format=SAGA type=$TYPE output=saga_export.sdat nodata=-9999	
	saga_cmd libta_preprocessor 5 -ELEV:saga_export.sgrd -FILLED:filled.sgrd -MINSLOPE:$GIS_OPT_SINKFILL_MIN_SLOPE

	## apply saga multi-directional lee filter if selected prior to rst
	if [ $GIS_FLAG_P = 1 ]; then
		##multi-directional lee filter
		saga_cmd libgrid_filter 3 -INPUT:filled.sgrd -RESULT:filled_filtered.sgrd -NOISE_ABS:1.0 -NOISE_REL:1.0 -WEIGHTED -METHOD:2


		#import filtered to GRASS
		r.in.gdal -o input=filled_filtered.sdat output=${ELEV_RASTER}_saga_pre
	else
		#import filtered to GRASS
		r.in.gdal -o input=filled.sdat output=${ELEV_RASTER}_saga_pre
	fi 

	## r.random for % pts & v.surf.rst
	## --> to do: check input % and strip 
	r.random -b input=${ELEV_RASTER}_saga_pre n=${GIS_OPT_RANDOM_PTS}% vector_output=random_pts --overwrite
	v.surf.rst -t input=random_pts elev=${ELEV_RASTER}_rst zcolumn=value tension=$GIS_OPT_REMOVAL_RST_TENSION smooth=$GIS_OPT_REMOVAL_RST_SMOOTH

	##post multi-directional lee filter
	if [ $GIS_FLAG_F = 1 ];then
		r.out.gdal input=${ELEV_RASTER}_rst format=SAGA type=$TYPE output=saga_export.sdat nodata=-9999	
		##multi-directional filter
		saga_cmd libgrid_filter 3 -INPUT:saga_export.sgrd -RESULT:filtered.sgrd -NOISE_ABS:1.0 -NOISE_REL:1.0 -WEIGHTED -METHOD:2

		#import filtered to GRASS
		r.in.gdal -o input=filtered.sdat output=${ELEV_RASTER}_rst_post_filtered_lee
	fi

	## create difference map b/w input elev & interp
	r.mapcalc "${ELEV_RASTER}_rst_diff=${ELEV_RASTER}_rst - $GIS_OPT_REMOVAL_ELEVATION"
	r.colors map=${ELEV_RASTER}_rst_diff color=differences

	## create hs z4
	r.shaded.relief map=${ELEV_RASTER}_rst shadedmap=${ELEV_RASTER}_rst_hs4 zmult=4 --overwrite

	## create map depicting higher areas
	r.mapcalc "${ELEV_RASTER}_rst_higher=${ELEV_RASTER}_rst_diff>0"

	## --> to do: creation of additional local/regional maps to assist in determing surface form -- should be png/pdf in dir
	##		write out txt of -t tension
	##		optimize tenion & smoothing parameter ----> perhaps a series of maps generated with vary tension & r.series for std change?
	##		---> v.surf.rst has cross-validation
fi


##remove any mask if present
r.mask -r

