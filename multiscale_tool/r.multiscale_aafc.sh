#!/bin/bash

############################################################################
#
# MODULE:       	r.multi_terrain_analysis
# AUTHOR(S):    	richard burcher. (richardburcher@gmail.com).
# PURPOSE:      	multi-scale terrain analysis (varying neighborhood average filtering).
# COPYRIGHT:    	(C) 2009 GRASS Development Team/richard burcher
# DATE:			Summer 2011
# CONTRACTED BY:	AAFC -- CanSIS
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
#
############################################################################

## OVERVIEW:

##GRASS GIS script that applies varying multi-scale neighborhood average filter to input GRASS Raster to impose scale effects on output raster. 1st & 2nd order derivatives are calculated based on filtered rasters. Provide the basis for landform derivatives grouped into 1)Local, 2)Global & 3) Segmentation outputs. Univarate statistics are calculated for all derivative outputs, sorted by name & written to $OUTREPORT. Meta data for the input raster and recoded/reclassified derivatives outputs is written to $OUTREPORT2. Final derivatives are exported to ESRI GeoTiff.

## REQUIREMENTS:

##-Must be inside a GRASS shell.
##-Input raster must be readable by GDAL.
##-Built & tested with GRASS 6.4.2 compiled from July 9 2011 SVN snapshot used.
## R > 2.10
## SAGA > 2.07
## write permissions in directory where running for output files (txt/geotiff etc)

## INSTALLATION:
## install to grass /scripts directory. make executable chmod +ax [file].

## USAGE:
## more appropiate for GUI operation. at grass command prompt type: r.multiscale_aafc.sh to launch GUI.


## ============================================================================
## ============================================================================

### GRASS GUI 

#%Module
#% description: GRASS raster map multi-scale terrain analysis.
#% keywords: raster, multi-scale,terrain
#%End

## requried inputs ------------------------------------------------------------

#%Option
#% key: input
#% type: string
#% required: yes
#% multiple: no
#% description: Input Elevation Raster
#% gisprompt: old,cell,raster
#%End

## optional inputs ------------------------------------------------------------

#%Option
#% key: water_mask
#% type: string
#% required: no
#% multiple: no
#% description: Raster Mask (Only process area within mask).
#% guisection: Optional_Inputs
#% gisprompt: old,cell,raster
#%End

#%Option
#% key: filter_iterations
#% type: string
#% required: no
#% multiple: no
#% description: Range of Filter Neighborhoods. (Odd Integer only. Separate with space, ensure no space after last input).
#% answer: 0
#% guisection: Optional_Inputs
#%End

#%Option
#% key: filter_iterations_type
#% type: string
#% required: no
#% multiple: no
#% description: Type of Filter Range Neighborhood to Apply to Input Raster.
#% options: average,median,stddev,mode
#% answer: average
#% guisection: Optional_Inputs
#%End

#%Flag
#% key: i
#% description: Invert Raster Mask: (Only process area outside of mask. Excludes area within mask).
#% guisection: Optional_Inputs
#%End

## derivatives -------------------------------------------------------------------

#%Option
#% key: r_surface_roughness_grid
#% type: integer
#% required: no
#% multiple: no
#% description: Surface Roughness: Grid size in meters to calculate r.roughness.
#% answer: 400
#% guisection: Derivatives
#%End

#%Option
#% key: min_slp_allowed
#% type: double
#% required: no
#% multiple: no
#% description:  Minimum slope (in percent) for which aspect is computed.
#% answer: 0.1
#% guisection: Derivatives
#%End

#%Option
#% key: v_distance
#% type: double
#% required: no
#% multiple: no
#% description:  Vertical Distance for Downslope Index (Calculated using SAGA).
#% answer: 10.0
#% guisection: Derivatives
#%End

#%Option
#% key: pennock_slope_gradient
#% type: double
#% required: no
#% multiple: no
#% description: Pennock Classification: Slope Gradient to Define "Level".
#% answer: 3.0
#% guisection: Derivatives
#%End

#%Flag
#% key: v
#% description: Surface Roughness (planar/real). (Very Time intensive).
#% guisection: Derivatives
#%End

#%Flag
#% key: t
#% description: TWI (ln(a/(tanB)). (Time intensive).
#% guisection: Derivatives
#%End

#%Flag
#% key: f
#% description: Morphological Features (Morphometric features: peaks, ridges, passes, channels, pits and planes). (Time intensive).
#% guisection: Derivatives
#%End


#### mvrbf --------------------------------------------------------------

## TODO:remove comments when client signs off
## new tab for saga multiresolution valley flatness index.
## may be temp, depending on clients thoughts


#%Flag
#% key: sa
#% description: Calculate
#% guisection: MRVBF
#%End

#%Option
#% key: mrvbf_initial_thresold_slope
#% type: double
#% required: no
#% multiple: no
#% description: Initial slope threshold 
#% options:0.0 - 100.0
#% answer: 16.0
#% guisection: MRVBF
#%End

#%Option
#% key: mrvbf_threshold_elevation_percentile_lowness
#% type: double
#% required: no
#% multiple: no
#% description: Threshold for elevation percentile (lowness) 
#% options:0.0 - 1.0
#% answer: 0.4
#% guisection: MRVBF
#%End

#%Option
#% key: mrvbf_threshold_elevation_percentile_upness
#% type: double
#% required: no
#% multiple: no
#% description: Threshold for elevation percentile (upness) 
#% options:0.0 - 1.0
#% answer: 0.35
#% guisection: MRVBF
#%End

#%Option
#% key: mrvbf_shape_parameter_slope
#% type: double
#% required: no
#% multiple: no
#% description: Threshold for elevation percentile (upness) 
#% options:0.0 - 100.0
#% answer: 4.0
#% guisection: MRVBF
#%End

#%Option
#% key: mrvbf_shape_parameter_elevation_percentile
#% type: double
#% required: no
#% multiple: no
#% description: Threshold for shape parameter for elevation percentile 
#% options:0.0 - 100.0
#% answer: 3.0
#% guisection: MRVBF
#%End

#%Option
#% key: mrvbf_maximum_resolution
#% type: double
#% required: no
#% multiple: no
#% description: Threshold for shape parameter for elevation percentile 
#% options:0.0 - 100.0
#% answer: 100.0
#% guisection: MRVBF
#%End


#### segmentations --------------------------------------------------------------


## ==== Iwahashi/Pike

#%Flag
#% key: s
#% description: Calculate
#% guisection: Segmentation_IP
#%End

#%Option
#% key: iwahashi_pike_nested_means
#% type: string
#% required: no
#% multiple: no
#% description: Iwahashi/Pike: Classification Type. (All = 99)
#% options: 8,12,16,99
#% answer: 8
#% guisection: Segmentation_IP
#%End

## ==== Cluster with R using Clara & randomForest

#%Flag
#% key: a
#% description: Calculate     ----- Select inputs from checkbox below for model inputs.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: k
#% description: elevation
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: b
#% description: slope
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: c
#% description: aspect_azimuth
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: d
#% description: pcurv
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: g
#% description: tcurv
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: h
#% description: rhpca
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: j
#% description: downslope_index
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: l
#% description: elevation_relief_ratio
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: r
#% description: pennock
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: m
#% description: morphological_features   --- Must select to be calculated in 'Derviative tab'
#% guisection: Segmentation_Clara_randomForest
#%End

#%Flag
#% key: n
#% description: surface_roughness   --- Must select to be calculated in 'Derviative tab'
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_raster1
#% gisprompt: string
#% type: string
#% description: Raster #1 to be reclassified. Spell exact as shown for check-box.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_file1
#% gisprompt: old_file,file,input
#% type: string
#% description: Input Text Files for Raster #1 reclassification.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_raster2
#% gisprompt: string
#% type: string
#% description: Raster #2 to be reclassified. Spell exact as shown for check-box.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_file2
#% gisprompt: old_file,file,input
#% type: string
#% description: Input Text Files for Raster #2 reclassification.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_raster3
#% gisprompt: string
#% type: string
#% description: Raster #3 to be reclassified. Spell exact as shown for check-box.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_file3
#% gisprompt: old_file,file,input
#% type: string
#% description: Input Text Files for Raster #3 reclassification.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_raster4
#% gisprompt: string
#% type: string
#% description: Raster #4 to be reclassified. Spell exact as shown for check-box.
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_reclass_file4
#% gisprompt: old_file,file,input
#% type: string
#% description: Input Text Files for Raster #4 reclassification.
#% guisection: Segmentation_Clara_randomForest
#%End
#%Option
#% key: cluster_sample_points
#% type: integer
#% description: Number of random sample points to classify.
#% answer: 500
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_number_classes
#% type: integer
#% description: Number of cluster classes.
#% answer: 5
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_number_trees
#% type: integer
#% description: Number of randomForest trees to generate.
#% answer: 200
#% guisection: Segmentation_Clara_randomForest
#%End

#%Option
#% key: cluster_neighbors_windowsize
#% type: integer
#% description: Size of window to apply "mode" neighborhood to final product. Odd integer.
#% answer: 5
#% guisection: Segmentation_Clara_randomForest
#%End


## Optional ----------------------------------------------------------------------

##%Flag
##% key: q
##% description: Quiet
##%End

#%Flag
#% key: e
#% description: Export GRASS Rasters to ESRI GeoTiff's.
##% guisection: Optional_Outputs
#%End

#%Flag
#% key: p
#% description: Export PNG of Final Rasters from Current MAPSET.
##% guisection: Optional_Outputs
#%End

#%Flag
#% key: z
#% description: Generate Profile Plots of Input Raster in N/S and E/W orientations.
##% guisection: Optional_Outputs
#%End

#%Option
#% key: profile_distance
#% type: integer
#% required: no
#% multiple: no
#% answer: 200
#% description: Spacing Interval to Generate Profile Plots of Input Raster in N/S and E/W orientations. (Integer only).
#% End

## ============================================================================
## ============================================================================

if [ -z "$GISBASE" ] ; then
    echo "You must be in GRASS GIS to run this program." 1>&2
    exit 1
fi

if [ "$1" != "@ARGS_PARSED@" ] ; then
    exec g.parser "$0" "$@"
fi

#check number of args supplied to script on cmd
if [ $# = 0 ]; then
	printf "Usage: %s (at GRASS prompt to use GUI)" "$(basename $0)" 	
	exit 1
fi

##=============================================================================


##local variables
OUTDIR=
ASPECT_CARDINAL_DIRECTION=

## check inputs to GUI
RASTER=$GIS_OPT_INPUT

FILTER_ITERATIONS=$GIS_OPT_FILTER_ITERATIONS
MIN_SLOPE_ALLOWED=$GIS_OPT_MIN_SLP_ALLOWED
PROMINENCE_RADIUS=$GIS_OPT_R_PROMINENCE_RADIUS
IWAHASHI_PIKE_CLASSES=$GIS_OPT_IWAHASHI_PIKE_NESTED_MEANS
EXPORT=1
DISPLAY=1
MASK_WATER=$GIS_OPT_WATER_MASK

FILTER_ITERATIONS_TYPE=$GIS_OPT_FILTER_ITERATIONS_TYPE

##=============================================================================
##=============================================================================

## set directory output location
#remove '@' from raster name
OUTDIR=${RASTER%@*}.$$

echo $VIEWER $EXPORT $VERBOSE $MIN_SLOPE_ALLOWED
echo "raster entered: $RASTER"
echo "min slope: $MIN_SLOPE_ALLOWED"
echo "raster dir: $OUTDIR"
echo "mask: $MASK_WATER"
echo "filter iterations: $FILTER_ITERATIONS"
echo "prominence radius: $PROMINENCE_RADIUS"
echo "outdir: $OUTDIR"


## GRASS settings

##set region
##determine raster resolution to set region to resolution. export issues arise if not set. ie export to saga will be problematic is n/s & e/w res diff
RASTER_RESOLUTION=`r.info -s $RASTER | grep nsres | awk -F"=" '{print $2}'`
echo "raster res is: $RASTER_RESOLUTION"
g.region rast=$RASTER res=$RASTER_RESOLUTION -ap

##set overwrite explicitly
g.gisenv set=OVERWRITE=1

#export GRASS enviroments vars
eval `g.gisenv`

# grass png driver settings 
export GRASS_TRUECOLOR=TRUE
export GRASS_WIDTH=1600
export GRASS_HEIGHT=1200


##remove all rasters prior to running tool
echo "deleting all rasters in mapset prior to tool operations"
g.mremove -f rast=*
g.mremove -f rast=*


##apply water mask if avail
##if [ $GIS_FLAG_I = 1 -a "$GIS_OPT_WATER_MASK" != "" ]; then
##	 invert the raster mask. raster supplied is not processed. ie) hydrology areas, buildings etc
##	echo "inverted mask applied to all raster operations"
##	r.mask -i $GIS_OPT_WATER_MASK
##elif [ "$GIS_OPT_WATER_MASK" != "" ]; then
##	set supplied mask for all raster operations
##	echo "mask applied to all raster operations"	
##	r.mask $GIS_OPT_WATER_MASK

##	echo "water mask applied is: $GIS_OPT_WATER_MASK"
##fi

##=============================================================================
##=============================================================================

## create output folder & text files for recode/reclassifying

#create output directory to store report/exported data
mkdir -p ${OUTDIR}/graphics/landscape_elevation_shades
mkdir -p ${OUTDIR}/graphics/density_plots
mkdir -p ${OUTDIR}/graphics/profile_plots
mkdir -p ${OUTDIR}/graphics/derivatives_segmentations_variability_maps
mkdir -p ${OUTDIR}/geotiffs
mkdir -p ${OUTDIR}/descrip
mkdir -p ${OUTDIR}/input_txt_files
mkdir -p ${OUTDIR}/tmp

##directory vars
OUTDIR_PNGS=${OUTDIR}/graphics/derivatives_segmentations_variability_maps
OUTDIR_DENSITY_PLOTS=${OUTDIR}/graphics/density_plots
OUTDIR_PROFILE_PLOTS=${OUTDIR}/graphics/profile_plots

#output text reports
CSV_DERV_STATS=${OUTDIR}/descrip/final_deriv_stats.csv
META_DERV=${OUTDIR}/descrip/final_deriv_metadata.txt

#iwahashi/pike laplacian filter. need full path to filter to work correctly through GRASS GUI
IP_LAPLACIAN=`pwd`/${OUTDIR}/input_txt_files/laplacian.asc

#create iwahashi/pike laplacian 4 based filter
echo -e 'TITLE 3*3 Laplacian\nMATRIX 3\n0 -1 0\n-1 4 -1\n0 -1 0\nDIVISOR 1\nTYPE P' > $IP_LAPLACIAN

#input txt files
RECLASS_ASPECT=${OUTDIR}/input_txt_files/reclass.aspect
RECODE_ASPECT=${OUTDIR}/input_txt_files/recode.aspect
RECLASS_RHPCA=${OUTDIR}/input_txt_files/reclass.rhpca

#r.recode aspect inputs & reclass textual descrip. ---->not using at moment
echo 0.:360.:1:8 > $RECODE_ASPECT
##touch reclass.aspect; echo -e '1=1 E\n''2=2 NE\n''3=3 N\n''4=4 NW\n''5=5 W\n''6=6 SW\n''7=7 S\n''8=8 SE' > reclass.aspect
echo -e '0 thru 45 = 1 North\n45 thru 135 = 2 East\n135 thru 225 = 3 South\n225 thru 315 = 4 West\n 315 thru 360 = 1 North' > $RECLASS_ASPECT

#rhpca reclassify into categories
echo -e '1=1 Upper\n''2=2 Upper Middle\n''3=3 Middle\n''4=4 Lower Middle\n''5=5 Lower' > $RECLASS_RHPCA

#header of csv derv stats report
DERIVATIVE_HEADER='derviv_name\tn\tnull_cells\tcells\tmin\tmax\trange\tmean\tmean_of_abs\tstd\tdev_variance\tcoeff_var\tsum\tfirst_quartile\tmedian\tthird_quartile\tpercentile_90'

##dave kroetsch soil organic carbon add-ins
#reclassify pennock
RECLASS_PENNOCK=${OUTDIR}/input_txt_files/reclass.pennock
echo -e '1=1 CFS\n2=2 DFS\n3=3 CSH\n4=4 DSH\n5=5 CBS\n6=6 DBS\n7=7 Level' > $RECLASS_PENNOCK


##=============================================================================
##=============================================================================

##functions


##/////////////////////////////////////////////////////////////////////////////

iwahashi_pike(){

## script calculates Iwahashi/Pike unsupervised nested-means algorithm using a three part geometric signature
## ---> need attribution

echo "calculating ip segmentation"

##recieve arguments
ITERATION=$1
INPUT=$2

echo $ITERATION'\t'$INPUT

##remove prior MASK
#r.mask -r

##slope
r.slope.aspect elevation=$INPUT slope=simg --overwrite

##convex area
#img1
r.mfilter.fp in=$INPUT out=f_laplacian filter=$IP_LAPLACIAN --overwrite
r.neighbors in=f_laplacian out=avg_laplacian --overwrite
r.mapcalc "img1=if(avg_laplacian,1,0,0)"
#convex
r.neighbors -c in=img1 out=convex size=11 --overwrite

##pits/peaks
#img2
r.neighbors in=$INPUT out=img2 method=median --overwrite
#img3
r.mapcalc "img3=float(if(($INPUT-img2),1,0,0) + if((img2-$INPUT),1,0,0))"
#pitpeak
r.neighbors -c in=img3 out=pitpeak size=11 --overwrite

##=============================================================================

class8() {

echo "calculating 8 classes"

##create water mask
#take rasterized waterbodies and inverts area. based on the nhn rasterization process of
#v.to.rast 'input' use=val value=1

#apply water mask if present
#if [ "$MASK_WATER" != "" ]; then
#	r.mask -i $MASK_WATER -o
#	echo "water mask present"
#else
#	echo "no water mask applied"
#fi

##img4
#calc zonalmean of slope w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=simg output=${OUTDIR}/input_txt_files/ip_8_simg_zonal_$ITERATION.txt
#parse for mean value of slope with in the MASK
VAL_SIMG_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_8_simg_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo "the zonal mean for simg is: $VAL_SIMG_ZONE"
r.mapcalc "img4=if(simg > $VAL_SIMG_ZONE,1,0)"

##img5
#calc zonalmean of convex w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=convex output=${OUTDIR}/input_txt_files/ip_8_convex_zonal_$ITERATION.txt
#parse for mean value of slope with in the MASK
VAL_CONVEX_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_8_convex_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo "the zonal mean for convex is: $VAL_CONVEX_ZONE"
r.mapcalc "img5=if(convex > $VAL_CONVEX_ZONE,1,0)"

##img6
#calc zonalmean of pitpeak w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=pitpeak output=${OUTDIR}/input_txt_files/ip_8_pitpeak_zonal_$ITERATION.txt
#parse for mean value of pitpeak with in the MASK
VAL_PITPEAK_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_8_pitpeak_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo "the zonal mean for pitpeak is: $VAL_PITPEAK_ZONE"
#r.mapcalc "img6=$VAL_PITPEAK_ZONE > pitpeak"
r.mapcalc "img6=if(pitpeak > $VAL_PITPEAK_ZONE,1,0)"


##calc classes
r.mapcalc "class1 = if(img4==1&&img5==1&&img6==1,1)"
r.mapcalc "class2 = if(img4==1&&img5==1&&img6==0,2)"
r.mapcalc "class3 = if(img4==1&&img5==0&&img6==1,3)"
r.mapcalc "class4 = if(img4==1&&img5==0&&img6==0,4)"
r.mapcalc "class5 = if(img4==0&&img5==1&&img6==1,5)"
r.mapcalc "class6 = if(img4==0&&img5==1&&img6==0,6)"
r.mapcalc "class7 = if(img4==0&&img5==0&&img6==1,7)"
r.mapcalc "class8 = if(img4==0&&img5==0&&img6==0,8)"

r.mapcalc "IP_Class8_$ITERATION=class1+class2+class3+class4+class5+class6+class7+class8"

##category labels
echo -e "1:steep/fine texture/high convexity\n2:steep/coarse texture/high convexity\n3:steep/fine texture/low convexity\n4:steep/coarse texture/low convexity\n5:gentle/fine texture/high convexity\n6:gentle/coarse texture/high convexity\n7:gentle/fine texture/low convexity\n8:gentle/coarse texture/low convexity" > ${OUTDIR}/input_txt_files/legend_IP_Class8.txt

r.category map=IP_Class8_$ITERATION rules=${OUTDIR}/input_txt_files/legend_IP_Class8.txt


echo "8 class completed"

##remove prior MASK
r.mask -r

#clean up temp rast
#g.mremove -f rast=class[1-8]
}


###============================================================================

class12(){

echo "calculating 12 classes"

##create water mask
#take rasterized waterbodies and inverts area. based on the nhn rasterization process of
#v.to.rast 'input' use=val value=1

##apply water mask if present
#if [ "$MASK_WATER" != "" ]; then
#	r.mask -i $MASK_WATER -o
#	echo "water mask present"
#else
#	echo "no water mask applied"
#fi

##img4
#calc zonalmean of slope w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=simg output=${OUTDIR}/input_txt_files/ip_12_simg_zonal_$ITERATION.txt
#parse for mean value of slope with in the MASK
VAL_SIMG_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_12_simg_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_SIMG_ZONE
r.mapcalc "img4=if(simg > $VAL_SIMG_ZONE,1,0)"

##img5
#calc zonalmean of convex w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=convex output=${OUTDIR}/input_txt_files/ip_12_convex_zonal_$ITERATION.txt
#parse for mean value of slope with in the MASK
VAL_CONVEX_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_12_convex_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_CONVEX_ZONE
r.mapcalc "img5=if(convex > $VAL_CONVEX_ZONE,1,0)"

##img6
#calc zonalmean of pitpeak w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=pitpeak output=${OUTDIR}/input_txt_files/ip_12_pitpeak_zonal_$ITERATION.txt
#parse for mean value of pitpeak with in the MASK
VAL_PITPEAK_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_12_pitpeak_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_PITPEAK_ZONE
#r.mapcalc "img6=$VAL_PITPEAK_ZONE > pitpeak"
r.mapcalc "img6=if(pitpeak > $VAL_PITPEAK_ZONE,1,0)"



##calc first classes
r.mapcalc "class1 = if(img4==1&&img5==1&&img6==1,1,0)"
r.mapcalc "class2 = if(img4==1&&img5==1&&img6==0,2,0)"
r.mapcalc "class3 = if(img4==1&&img5==0&&img6==1,3,0)"
r.mapcalc "class4 = if(img4==1&&img5==0&&img6==0,4,0)"

r.mapcalc "map1_4=class1+class2+class3+class4"

##=============================================================================

##mask alteration to exclude areas of img4
r.mapcalc "mask2=if(img4==1,null(),1)"
#replace nhn mask with mask2
r.mask input=mask2 -o

### new mask used for calc
##img7
#calc zonalmean of slope w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=simg zones=MASK output=simg_zonal.txt
#parse for mean value of slope with in the MASK
VAL_SIMG_ZONE=`grep mean= simg_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_SIMG_ZONE
r.mapcalc "img7_t=MASK*($VAL_SIMG_ZONE > simg)"
r.mapcalc "img7=if(isnull(img7_t),0,img7_t)"


##img8
#calc zonalmean of convex w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=convex zones=MASK output=convex_zonal.txt
#parse for mean value of slope with in the MASK
VAL_CONVEX_ZONE=`grep mean= convex_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_CONVEX_ZONE
r.mapcalc "img8_t=MASK*($VAL_CONVEX_ZONE > convex)"
r.mapcalc "img8=if(isnull(img8_t),0,img8_t)"

##img9
#calc zonalmean of pitpeak w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=pitpeak zones=MASK output=pitpeak_zonal.txt
#parse for mean value of pitpeak with in the MASK
VAL_PITPEAK_ZONE=`grep mean= pitpeak_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_PITPEAK_ZONE
r.mapcalc "img9_t=MASK*($VAL_PITPEAK_ZONE > pitpeak)"
r.mapcalc "img9=if(isnull(img9_t),0,img9_t)"

##=============================================================================

##calc second classes

r.mapcalc "class5 = if(img7==1&&img8==1&&img9==1,5,0)"
r.mapcalc "class6 = if(img7==1&&img8==1&&img9==0,6,0)"
r.mapcalc "class7 = if(img7==1&&img8==0&&img9==1,7,0)"
r.mapcalc "class8 = if(img7==1&&img8==0&&img9==0,8,0)"
r.mapcalc "class9 = if(img7==0&&img8==1&&img9==1,9,0)"
r.mapcalc "class10 = if(img7==0&&img8==1&&img9==0,10,0)"
r.mapcalc "class11 = if(img7==0&&img8==0&&img9==1,11,0)"
r.mapcalc "class12 = if(img7==0&&img8==0&&img9==0,12,0)"

r.mapcalc "map5_12=class5+class6+class7+class8+class9+class10+class11+class12"

##remove prior MASK
r.mask -r

##recode classes 5-12, to replace mask nulls with 0
r.mapcalc "map5_12_recode=if(isnull(map5_12),0,map5_12)"


##final map
r.mapcalc "IP_Class12_$ITERATION=map1_4+map5_12_recode"

##category labels
echo -e "1:steep/fine texture/high convexity\n2:steep/coarse texture/high convexity\n3:steep/fine texture/low convexity\n4:steep/coarse texture/low convexity\n5:moderately gentle/fine texture/high convexity\n6:moderately gentle/coarse texture/high convexity\n7:moderately gentle /fine texture/low convexity\n8:moderately gentle/coarse texture/low convexity\n9:gentle/fine texture/high convexity\n10:gentle/coarse texture/high convexity\n11:gentle/fine texture/low convexity\n12:gentle/coarse texture/low convexity" > ${OUTDIR}/input_txt_files/legend_IP_Class12.txt

r.category map=IP_Class12_$ITERATION rules=${OUTDIR}/input_txt_files/legend_IP_Class12.txt

echo "12 class completed"

##remove prior MASK
r.mask -r

}

###============================================================================

class16(){

echo "calculating 16 classes"

##create water mask
#take rasterized waterbodies and inverts area. based on the nhn rasterization process of
#v.to.rast 'input' use=val value=1

##apply water mask if present
#if [ "$MASK_WATER" != "" ]; then
#	r.mask -i $MASK_WATER -o
#	echo "water mask present"
#else
#	echo "no water mask applied"
#fi


##img4
#calc zonalmean of slope w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=simg output=${OUTDIR}/input_txt_files/ip_16_simg_zonal_$ITERATION.txt
#parse for mean value of slope with in the MASK
VAL_SIMG_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_16_simg_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_SIMG_ZONE
r.mapcalc "img4=if(simg > $VAL_SIMG_ZONE,1,0)"

##img5
#calc zonalmean of convex w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=convex output=${OUTDIR}/input_txt_files/ip_16_convex_zonal_$ITERATION.txt
#parse for mean value of slope with in the MASK
VAL_CONVEX_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_16_convex_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_CONVEX_ZONE
r.mapcalc "img5=if(convex > $VAL_CONVEX_ZONE,1,0)"

##img6
#calc zonalmean of pitpeak w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=pitpeak output=${OUTDIR}/input_txt_files/ip_16_pitpeak_zonal_$ITERATION.txt
#parse for mean value of pitpeak with in the MASK
VAL_PITPEAK_ZONE=`grep mean= ${OUTDIR}/input_txt_files/ip_16_pitpeak_zonal_$ITERATION.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_PITPEAK_ZONE
#r.mapcalc "img6=$VAL_PITPEAK_ZONE > pitpeak"
r.mapcalc "img6=if(pitpeak > $VAL_PITPEAK_ZONE,1,0)"

 

##calc first classes
r.mapcalc "class1 = if(img4==1&&img5==1&&img6==1,1,0)"
r.mapcalc "class2 = if(img4==1&&img5==1&&img6==0,2,0)"
r.mapcalc "class3 = if(img4==1&&img5==0&&img6==1,3,0)"
r.mapcalc "class4 = if(img4==1&&img5==0&&img6==0,4,0)"

r.mapcalc "map1_4=class1+class2+class3+class4"

##=============================================================================

##mask alteration to exclude areas of img4
r.mapcalc "mask2=if(img4==1,null(),1)"
#replace nhn mask with mask2
r.mask input=mask2 -o

### new mask used for calc
##img7
#calc zonalmean of slope w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=simg zones=MASK output=simg_zonal.txt
#parse for mean value of slope with in the MASK
VAL_SIMG_ZONE=`grep mean= simg_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_SIMG_ZONE
r.mapcalc "img7_t=MASK*($VAL_SIMG_ZONE > simg)"
r.mapcalc "img7=if(isnull(img7_t),0,img7_t)"


##img8
#calc zonalmean of convex w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=convex zones=MASK output=convex_zonal.txt
#parse for mean value of slope with in the MASK
VAL_CONVEX_ZONE=`grep mean= convex_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_CONVEX_ZONE
r.mapcalc "img8_t=MASK*($VAL_CONVEX_ZONE > convex)"
r.mapcalc "img8=if(isnull(img8_t),0,img8_t)"

##img9
#calc zonalmean of pitpeak w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=pitpeak zones=MASK output=pitpeak_zonal.txt
#parse for mean value of pitpeak with in the MASK
VAL_PITPEAK_ZONE=`grep mean= pitpeak_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_PITPEAK_ZONE
r.mapcalc "img9_t=MASK*($VAL_PITPEAK_ZONE > pitpeak)"
r.mapcalc "img9=if(isnull(img9_t),0,img9_t)"

##=============================================================================

##calc second classes

r.mapcalc "class5 = if(img7==1&&img8==1&&img9==1,5,0)"
r.mapcalc "class6 = if(img7==1&&img8==1&&img9==0,6,0)"
r.mapcalc "class7 = if(img7==1&&img8==0&&img9==1,7,0)"
r.mapcalc "class8 = if(img7==1&&img8==0&&img9==0,8,0)"

r.mapcalc "map5_8=class5+class6+class7+class8"

##remove prior MASK
r.mask -r

##recode classes 5-12, to replace mask nulls with 0
r.mapcalc "map5_8_recode=if(isnull(map5_8),0,map5_8)"


##map1_8
r.mapcalc "map1_8=map1_4+map5_8_recode"

##=============================================================================

##calc third classes

##mask alteration to exclude areas of img4 + img7
r.mapcalc "mask3=if((img4+img7)==1,null(),1)"
#replace nhn mask with mask2
r.mask input=mask3 -o

### new mask used for calc
##img10
#calc zonalmean of slope w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=simg zones=MASK output=simg_zonal.txt
#parse for mean value of slope with in the MASK
VAL_SIMG_ZONE=`grep mean= simg_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_SIMG_ZONE
r.mapcalc "img10_t=MASK*($VAL_SIMG_ZONE > simg)"
r.mapcalc "img10=if(isnull(img10_t),0,img10_t)"


##img11
#calc zonalmean of convex w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=convex zones=MASK output=convex_zonal.txt
#parse for mean value of slope with in the MASK
VAL_CONVEX_ZONE=`grep mean= convex_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_CONVEX_ZONE
r.mapcalc "img11_t=MASK*($VAL_CONVEX_ZONE > convex)"
r.mapcalc "img11=if(isnull(img11_t),0,img11_t)"

##img12
#calc zonalmean of pitpeak w/MASK. calc r.univar, export txt & parse.
#r.statistics does not permit fp.
r.univar -g map=pitpeak zones=MASK output=pitpeak_zonal.txt
#parse for mean value of pitpeak with in the MASK
VAL_PITPEAK_ZONE=`grep mean= pitpeak_zonal.txt | awk 'BEGIN {FS = "="}; {print $2}'`
echo $VAL_PITPEAK_ZONE
r.mapcalc "img12_t=MASK*($VAL_PITPEAK_ZONE > pitpeak)"
r.mapcalc "img12=if(isnull(img12_t),0,img12_t)"


r.mapcalc "class9 = if(img10==1&&img11==1&&img12==1,9,0)"
r.mapcalc "class10 = if(img10==1&&img11==1&&img12==0,10,0)"
r.mapcalc "class11 = if(img10==1&&img11==0&&img12==1,11,0)"
r.mapcalc "class12 = if(img10==1&&img11==0&&img12==0,12,0)"
r.mapcalc "class13 = if(img10==0&&img11==1&&img12==1,13,0)"
r.mapcalc "class14 = if(img10==0&&img11==1&&img12==0,14,0)"
r.mapcalc "class15 = if(img10==0&&img11==0&&img12==1,15,0)"
r.mapcalc "class16 = if(img10==0&&img11==0&&img12==0,16,0)"

##remove prior MASK
r.mask -r

##map9_16
r.mapcalc "map9_16=class9+class10+class11+class12+class13+class14+class15+class16"

##recode classes 9-16, to replace mask nulls with 0
r.mapcalc "map9_16_recode=if(isnull(map9_16),0,map9_16)"


##final map
r.mapcalc "IP_Class16_$ITERATION=map1_4+map5_8_recode+map9_16_recode"

##category label
echo -e "1:steep/fine texture/high convexity\n2:steep/coarse texture/high convexity\n3:steep/fine texture/low convexity\n4:steep/coarse texture/low convexity\n5:moderately steep/fine texture/high convexity\n6:moderately steep/coarse texture/high convexity\n7:moderately steep /fine texture/low convexity\n8:moderately steep/coarse texture/low convexity\n9:moderately gentle/fine texture/high convexity\n10:moderately gentle/coarse texture/high convexity\n11:moderately gentle/fine texture/low convexity\n12:moderately gentle/coarse texture/low convexity\n13:gentle/fine texture/high convexity\n14:gentle/coarse texture/high convexity\n15:gentle/fine texture/low convexity\n16:gentle/coarse texture/low convexity" > ${OUTDIR}/input_txt_files/legend_IP_Class16.txt

r.category map=IP_Class16_$ITERATION rules=${OUTDIR}/input_txt_files/legend_IP_Class16.txt

echo "16 class completed"

##remove prior MASK
r.mask -r

}


##classes to calculate. default is 8 in GRASS GUI
if [ "$IWAHASHI_PIKE_CLASSES" = "8" ]; then
	class8
elif [ "$IWAHASHI_PIKE_CLASSES" = "12" ]; then
	class12
elif [ "$IWAHASHI_PIKE_CLASSES" = "16" ]; then
	class16
elif [ "$IWAHASHI_PIKE_CLASSES" = "99" ]; then
	class8
	class12
	class16 
fi

}

##/////////////////////////////////////////////////////////////////////////////

clara_cluster_randomForest() {

## implements the R clara clustering object using the PAM algorithm & randomForest. a user selected random sample size is
## applied to input rasters. clara clustering object of n classes computed. model created by randomForest from this & solved for
## unsampled areas using predict. exported to GRASS where r.neighborhoods mode method applied to clean up product.

## inspiration for this from http://casoilresource.lawr.ucdavis.edu/drupal/node/993

i=$1

### export selected raster to tmp geotiffs
exportRasters=

if [ $GIS_FLAG_K = 1 ]; then
	exportRasters=${exportRasters}" Elevation_$i"
fi

if [ $GIS_FLAG_B = 1 ]; then
	exportRasters=${exportRasters}" Slope_$i"
fi

if [ $GIS_FLAG_C = 1 ]; then
	exportRasters=$exportRasters" Aspect_azimuth_$i"
fi

if [ $GIS_FLAG_D = 1 ]; then
	exportRasters=$exportRasters" Pcurv_$i"
fi

if [ $GIS_FLAG_G = 1 ]; then
	exportRasters=$exportRasters" Tcurv_$i"
fi

if [ $GIS_FLAG_H = 1 ]; then
	exportRasters=$exportRasters" Rhpca_log10_final_$i"
fi

if [ $GIS_FLAG_J = 1 ]; then
	exportRasters=$exportRasters" Downslope_index_$i"
fi

if [ $GIS_FLAG_M = 1 ]; then
	exportRasters=$exportRasters" Morphometric_features_$i"
fi

if [ $GIS_FLAG_N = 1 ]; then
	exportRasters=$exportRasters" Roughness_$i"
fi

if [ $GIS_FLAG_L = 1 ]; then
	exportRasters=$exportRasters" Elevation_relief_ratio_$i"
fi

if [ $GIS_FLAG_R = 1 ]; then
	exportRasters=$exportRasters" Pennock_$i"
fi

### reclassify selected rasters
if [ "$GIS_OPT_CLUSTER_RECLASS_RASTER1" != "" ]; then
	#reclass raster1
	r.reclass input="${GIS_OPT_CLUSTER_RECLASS_RASTER1^}"_$i output="${GIS_OPT_CLUSTER_RECLASS_RASTER1^}"_reclass_$i rules=$GIS_OPT_CLUSTER_RECLASS_FILE1 --overwrite
	#replace name for raster to be exported
	exportRasters=`echo -e $exportRasters | sed s/"${GIS_OPT_CLUSTER_RECLASS_RASTER1^}"_$i/"${GIS_OPT_CLUSTER_RECLASS_RASTER1^}"_reclass_$i/`

fi

if [ "$GIS_OPT_CLUSTER_RECLASS_RASTER2" != "" ]; then
	#reclass raster2
	r.reclass input="${GIS_OPT_CLUSTER_RECLASS_RASTER2^}"_$i output="${GIS_OPT_CLUSTER_RECLASS_RASTER2^}"_reclass_$i rules=$GIS_OPT_CLUSTER_RECLASS_FILE2 --overwrite
	#replace name for raster to be exported
	exportRasters=`echo -e $exportRasters | sed s/"${GIS_OPT_CLUSTER_RECLASS_RASTER2^}"_$i/"${GIS_OPT_CLUSTER_RECLASS_RASTER2^}"_reclass_$i/`

fi

if [ "$GIS_OPT_CLUSTER_RECLASS_RASTER3" != "" ]; then
	#reclass raster3
	r.reclass input="${GIS_OPT_CLUSTER_RECLASS_RASTER3^}"_$i output="${GIS_OPT_CLUSTER_RECLASS_RASTER3^}"_reclass_$i rules=$GIS_OPT_CLUSTER_RECLASS_FILE3 --overwrite
	#replace name for raster to be exported
	exportRasters=`echo -e $exportRasters | sed s/"${GIS_OPT_CLUSTER_RECLASS_RASTER3^}"_$i/"${GIS_OPT_CLUSTER_RECLASS_RASTER3^}"_reclass_$i/`

fi

if [ "$GIS_OPT_CLUSTER_RECLASS_RASTER4" != "" ]; then
	#reclass raster4
	r.reclass input="${GIS_OPT_CLUSTER_RECLASS_RASTER4^}"_$i output="${GIS_OPT_CLUSTER_RECLASS_RASTER4^}"_reclass_$i rules=$GIS_OPT_CLUSTER_RECLASS_FILE4 --overwrite
	#replace name for raster to be exported
	exportRasters=`echo -e $exportRasters | sed s/"${GIS_OPT_CLUSTER_RECLASS_RASTER4^}"_$i/"${GIS_OPT_CLUSTER_RECLASS_RASTER4^}"_reclass_$i/`

fi


### create txt file of output rasters. each raster name on sep line.
setDIR=$PWD/${OUTDIR}/tmp/
echo -e $exportRasters | tr " " "\n" | sed -e "s|^|$setDIR|" > ${OUTDIR}/input_txt_files/cluster_raster_input.txt
cat ${OUTDIR}/input_txt_files/cluster_raster_input.txt

### create txt file for R model
echo -e $exportRasters | sed -e "s/[[:space:]]/+/g" > ${OUTDIR}/input_txt_files/cluster_model.txt

### export as tmp geotiffs for import into R. rasterstack requires.
## transpose cluster_raster_input.txt
for e in `tr "\n" " " < ${OUTDIR}/input_txt_files/cluster_raster_input.txt`; do
	r.out.gdal input=`basename "$e"` type=Float32 output=$e nodata=-9999
done

## ---- R component
## build R string

## model str
modelStr=`echo $exportRasters | sed -e "s/[[:space:]]/+/g"`

exportR="library(cluster)\nlibrary(raster)\nlibrary(randomForest)\nfc<-file('"${OUTDIR}/input_txt_files/cluster_raster_input.txt"')\nimportedRasters <-readLines(fc)\nclose(fc)\ns<-stack(importedRasters)\nrandom.df <-as.data.frame(sampleRandom(s,size=$GIS_OPT_CLUSTER_SAMPLE_POINTS))\nrandom.df <-na.omit(random.df)\ns.clara <-clara(random.df,k=$GIS_OPT_CLUSTER_NUMBER_CLASSES,stand=T,pamLike=T)\nrandom.df\$cluster <- factor(s.clara\$clustering)\nwrite.table(summary(random.df),file='"${OUTDIR}/descrip/cluster_randomForest_summary_$i.txt"')\nrf <-randomForest(cluster ~ "$modelStr",data=random.df,ntree=$GIS_OPT_CLUSTER_NUMBER_TREES,importance=T)\np<-predict(s,rf,type='"response"',progress='"text"')\nwriteRaster(p,filename='"${OUTDIR}/tmp/Cluster_$i.tif"',format='"GTiff"',datatype='"INT1U"',overwrite=T,NAflag=-9999)\nimp<-importance(rf)\nwrite.table(imp,file='"${OUTDIR}/descrip/cluster_randomForest_importance_$i.txt"')\npng(file='"${OUTDIR}/descrip/plot_randomForest_variable_importance_$i.png"')\nvarImpPlot(rf)\ndev.off()"

echo -e $exportR | R --vanilla

###import raster back into grass
r.in.gdal -o input=${OUTDIR}/tmp/Cluster_$i.tif output=Cluster_$i --overwrite
r.colors map=Cluster_$i color=ryb

###apply neighborhood mode function to reduce isolated pixels.
r.neighbors input=Cluster_$i output=Cluster_$i.mode$GIS_OPT_CLUSTER_NEIGHBORS_WINDOWSIZE method=mode size=$GIS_OPT_CLUSTER_NEIGHBORS_WINDOWSIZE --overwrite
r.colors map=Cluster_$i.mode$GIS_OPT_CLUSTER_NEIGHBORS_WINDOWSIZE color=ryb

##ensure raster mask applied if appicable to outputs
r.mapcalc "Cluster_$i=Cluster_$i"
r.mapcalc "Cluster_$i.mode$GIS_OPT_CLUSTER_NEIGHBORS_WINDOWSIZE=Cluster_$i.mode$GIS_OPT_CLUSTER_NEIGHBORS_WINDOWSIZE"

}

##/////////////////////////////////////////////////////////////////////////////

r_roughness() {

# MODULE:	r.roughness
# AUTHOR(S):	Carlos H. Grohmann <carlos dot grohmann at gmail dot com >
# PURPOSE:	Calculates surface roughness from DEMs. (uses r.surf.area)
#		In this script surface roughness is used in the sense of 
#		Hobson (1972), who describes it as the ratio between surface 
#		(real) area and flat (plan) area of square cells; in this 
#		approach, flat surfaces would present values close to 1, 
#		whilst in irregular ones the ratio shows a curvilinear 
#		relationship which asymptotically approaches infinity as the 
#		real areas increases.
#		Reference:
#		Hobson, R.D., 1972. Surface roughness in topography: 
#		quantitative approach. In: Chorley, R.J. (ed) Spatial 
#		analysis in geomorphology. Methuer, London, p.225-245.
#
#		This script will create square sub-regions with size defined by
#		the option GRID. In each sub-region, the real and planar areas
#		will be calculated by r.surf.area, and the results (points at 
#		the center of sub-regions) will be interpolated with v.surf.rst.
#		The user also can set the tension and smooth parameters.
#
# COPYRIGHT:	(C) 2006-2009 by the GRASS Development Team
#
#		This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
# set environment so that awk works properly in all languages

unset LC_ALL
export LC_NUMERIC=C


TMP_ascii="`g.tempfile pid=$$`"
if [ $? -ne 0 ] || [ -z "${TMP_ascii}" ] ; then
    echo "ERROR: unable to create temporary files" 1>&2
    exit 1
fi


echo "inside r_rough function"


#vars for input var & output name
elev=Elevation_$1

echo "r_roughness raster is: $elev"

grid=$GIS_OPT_R_SURFACE_ROUGHNESS_GRID
#rough=$GIS_OPT_ROUGH

#---> added by richard burcher
ROUGHNESS=Roughness_$1
echo "roughness output is $ROUGHNESS"

R_ROUGHNESS_TENSION=40
R_ROUGHNESS_SMOOTH=0.1
#----->

#check if input file exists
#eval `g.findfile element=cell file=$elev`
#if [ -z "$name" ] ; then
#   echo "ERROR: map <$elev> not found."
#   exit 1
#fi

#if [ "$GIS_OPT_MAP" = "$GIS_OPT_ROUGH" ]; then
#	echo ""
#	echo "Input elevation map and output roughness map must have different names"
#	exit 1
#fi

#if [ -z "$GIS_OPT_ROUGH" ]; then
#    ROUGHNESS="${elev}_roughness_${grid}"
#else
#    ROUGHNESS="$GIS_OPT_ROUGH"
#fi

#######################################################################
cleanup() 
{
    eval `g.findfile elem=windows file="tmp_region.$$" | grep '^name='`
    if [ -n "$name" ] ; then
	unset WIND_OVERRIDE
	g.remove region="tmp_region.$$" --quiet
    fi
    rm -f "$TMP_ascii"
    g.remove vect="TMP_vect_$$" --quiet
}

# what to do in case of user break:
exitprocedure()
{
    echo "User break!"
    cleanup
    exit 1
}
# shell check for user break (signal list: trap -l)
trap "exitprocedure" 2 3 15

#######################################################################

########################################################################
# get region limits
maxnorth="`g.region -p | grep north | sed -e s/.*:\ *//`"
maxsouth="`g.region -p | grep south | sed -e s/.*:\ *//`"
maxwest="` g.region -p | grep west | sed -e s/.*:\ *//`"
maxeast="` g.region -p | grep east | sed -e s/.*:\ *//`"

echo "region limits are: $maxnorth $maxsouth $maxwest $maxeast"



# setup internal region
g.region save="tmp_region.$$"
WIND_OVERRIDE="tmp_region.$$"
export WIND_OVERRIDE

ns_dist="`echo $maxnorth $maxsouth | awk '{printf("%f", $1 - $2);}'`"
ew_dist="`echo $maxeast $maxwest | awk '{printf("%f", $1 - $2);}'`"
rows="`echo $ns_dist $grid | awk '{printf("%.0f", $1 / $2);}'`"
cols="`echo $ew_dist $grid | awk '{printf("%.0f", $1 / $2);}'`"

########################################################################

north=$maxnorth
west=$maxwest
south="`echo $north $grid | awk '{printf("%f", $1 - $2);}'`"
east="`echo $west $grid | awk '{printf("%f", $1 + $2);}'`"

# number of region
no_of_region="0"

### rows N-S
while [ `echo $south $maxsouth |awk '{printf("%d", $1 >= $2);}'` = 1 ];
do 
    echo "north -> south"    # 
    # columns W-E
    while [ `echo $east $maxeast |awk '{printf("%d", $1<= $2);}'` = 1 ];
    do
        echo "west -> east"  # 
       
        g.region n=$north s=$south w=$west e=$east

        dx="`echo $east $west |awk '{printf("%f", $1 - $2);}'`"
        dy="`echo $north $south |awk '{printf("%f", $1 - $2);}'`"
        coord_x="`echo $west $dx |awk '{printf("%f", $1 + $2);}'`"
        coord_y="`echo $north $dy |awk '{printf("%f", $1 - $2);}'`"

        planarea="`r.surf.area input=$elev | grep Current | sed -e s/.*:\ *//`"
        realarea="`r.surf.area input=$elev | grep Estimated | sed -e s/.*:\ *//`"

	echo "$coord_x $coord_y $realarea $planarea" | \
	   awk '{printf "%d %d %f\n", $1, $2, $3 / $4}'>> "$TMP_ascii"

        west=$east
        east="`echo $west $grid |awk '{printf("%f", $1 + $2);}'`"
        
        no_of_region="`echo $no_of_region |awk '{printf("%.0f", $1 + 1);}'`"
        regions_total="`echo $rows $cols |awk '{printf("%.0f", $1 * $2);}'`"
        echo "--------- REGION NUMBER $no_of_region OF $regions_total ----------"

    done
    
    north=$south
    south="`echo $north $grid |awk '{printf("%f", $1 - $2);}'`"
    
    # go west
    west=$maxwest
    east="`echo $west $grid |awk '{printf("%f", $1 + $2);}'`"
done


# back to original region
unset WIND_OVERRIDE
g.remove region="tmp_region.$$" --quiet


v.in.ascii input="$TMP_ascii" output="TMP_vect_$$" format=point \
   fs=space skip=0 x=1 y=2 z=3 cat=0 -z

v.surf.rst input="TMP_vect_$$" layer=0 elev="$ROUGHNESS" zmult=1.0 \
   tension="$R_ROUGHNESS_TENSION" smooth="$R_ROUGHNESS_SMOOTH"

r.colors "$ROUGHNESS" color=rainbow

##ensure raster mask applied if appicable to outputs
r.mapcalc "$ROUGHNESS=$ROUGHNESS"

# record metadata
#r.support "$ROUGHNESS" title="Relief roughness of \"$GIS_OPT_MAP\"" history=""
#r.support "$ROUGHNESS" history="grid size: $grid"


### cleaning
cleanup

#echo ""
#if [ -n "$GIS_OPT_ROUGH" ] ; then
#    echo "Surface roughness map created and named [$ROUGHNESS]."
#else
#    echo "Surface roughness map created and named [$ROUGHNESS]. Consider renaming."
#fi
echo "Done."

}

##/////////////////////////////////////////////////////////////////////////////

pennock_orginal() {
## calculate pennocks classification. based on orginial critera for landform elements

r.slope.aspect elevation=$2 slope=slope_pennock pcurv=pcurv_pennock tcurv=tcurv_pennock min_slp_allowed=$GIS_OPT_MIN_SLP_ALLOWED --overwrite

##"level"
levelParm=$GIS_OPT_PENNOCK_SLOPE_GRADIENT

## 7 landform elements
r.mapcalc "cfs=if(pcurv_pennock < -0.10 && tcurv_pennock < 0.00 && slope_pennock > $levelParm, 1)"
r.mapcalc "dfs=if(pcurv_pennock < -0.10 && tcurv_pennock > 0.00 && slope_pennock > $levelParm, 2)"
r.mapcalc "csh=if(pcurv_pennock > 0.10 && tcurv_pennock < 0.00 && slope_pennock > $levelParm, 3)"
r.mapcalc "dsh=if(pcurv_pennock > 0.10 && tcurv_pennock > 0.00 && slope_pennock > $levelParm, 4)"
r.mapcalc "cbs=if(pcurv_pennock > -0.10 && pcurv_pennock < 0.10 && tcurv_pennock < 0.00 && slope_pennock > $levelParm, 5)"
r.mapcalc "dbs=if(pcurv_pennock > -0.10 && pcurv_pennock < 0.10 && tcurv_pennock > 0.00 && slope_pennock > $levelParm, 6)"
r.mapcalc "level=if(slope_pennock < $levelParm, 7)"

r.mapcalc "pennock_tmp=(cfs+dfs+csh+dsh+cbs+dbs+level)"

#reclass for category labels
r.reclass input=pennock_tmp output=Pennock_$1 --overwrite < $RECLASS_PENNOCK

##ensure raster mask applied if appicable to outputs
r.mapcalc "Pennock_$1=Pennock_$1"

##add category labels
echo -e "1:convergent footslope (cfs)\n2:divergent footslope (dfs)\n3:convergent shoulder (csh)\n4:divergent shoulder (dsh)\n5:convergent backslope (cbs)\n6:divergent backslope (dbs)\n7:level (l)" > ${OUTDIR}/input_txt_files/legend_pennock_7_classes.txt

r.category map=Pennock_$1 rules=${OUTDIR}/input_txt_files/legend_pennock_7_classes.txt

}

elevation_relief_ratio() {
## equiv to the coeffienent of dissection. mathematically similar to hyposmetric curve

#create mean/max/min elevation raster. can not have size=0, size=1 causes NaN to occur.
if [ $1 == 0 ]; then
	s=3
else
	s=$1
fi

r.neighbors input=$2 output=elev_mean_$1 size=$s --overwrite
r.neighbors input=$2 output=elev_max_$1 method=maximum size=$s --overwrite
r.neighbors input=$2 output=elev_min_$1 method=minimum size=$s --overwrite

r.mapcalc "Elevation_relief_ratio_$1=((elev_mean_$1 - elev_min_$1)/(elev_max_$1 - elev_min_$1))"

}

downslopeIndex() {
##integration code b/w GRASS & SAGA to allow calculation of Downslope Index in SAGA.
## regional based dervivate
## A new topographic index to quantify downslope controls
#on local drainage
#K. N. Hjerdt,J. J. McDonnell,J. Seibert, and A. Rodhe

IN_GDAL_RASTER=$1
OUT_GDAL_RASTER=$IN_GDAL_RASTER
OUT_SAGA_RASTER=Downslope_index_$2
DISTANCE=$3

##export grass dem to saga native format
##check export data type
DT=`r.info -t $IN_GDAL_RASTER | awk -F"=" '{ print $2 }'`
	echo "export data type for $IN_GDAL_RASTER is $DT"	

	if [ "$DT" = "CELL" ]; then
		TYPE=Int16
	else
		TYPE=Float32
	fi

r.out.gdal input=$IN_GDAL_RASTER format=SAGA type=$TYPE output=$OUTDIR/tmp/$OUT_GDAL_RASTER.sdat nodata=-9999

##calculate downslope index. output:0 refers to "distance" output grid
saga_cmd ta_morphometry 9 -DEM:$OUTDIR/tmp/$OUT_GDAL_RASTER.sgrd -GRADIENT:$OUTDIR/tmp/$OUT_SAGA_RASTER -DISTANCE:$DISTANCE -OUTPUT:0

##import SAGA raster into GRASS
r.in.gdal -o input=$OUTDIR/tmp/$OUT_SAGA_RASTER.sdat output=${OUT_SAGA_RASTER/\.*} --overwrite

##ensure raster mask applied if appicable to outputs
r.mapcalc "Downslope_index_$2=Downslope_index_$2"

}


mrvbf_index() {
##integration code b/w GRASS & SAGA to allow calculation of MRVBF index  in SAGA.
## regional based dervivate

IN_GDAL_RASTER=$1
OUT_GDAL_RASTER=$IN_GDAL_RASTER
OUT_SAGA_RASTER=mrvbf_index_$2
DISTANCE=$3





##export grass dem to saga native format
##check export data type
DT=`r.info -t $IN_GDAL_RASTER | awk -F"=" '{ print $2 }'`
	echo "export data type for $IN_GDAL_RASTER is $DT"	

	if [ "$DT" = "CELL" ]; then
		TYPE=Int16
	else
		TYPE=Float32
	fi

r.out.gdal input=$IN_GDAL_RASTER format=SAGA type=$TYPE output=$OUTDIR/tmp/$OUT_GDAL_RASTER.sdat nodata=-9999

##calculate mrvbf index. output:0 refers to "distance" output grid
saga_cmd ta_morphometry 8 -DEM:$OUTDIR/tmp/$OUT_GDAL_RASTER.sgrd -GRADIENT:$OUTDIR/tmp/$OUT_SAGA_RASTER -DISTANCE:$DISTANCE -OUTPUT:0

##import SAGA raster into GRASS
r.in.gdal -o input=$OUTDIR/tmp/$OUT_SAGA_RASTER.sdat output=${OUT_SAGA_RASTER/\.*} --overwrite

##ensure raster mask applied if appicable to outputs
r.mapcalc "mrvbf_index_$2=mrvbf_index_$2"

}


##/////////////////////////////////////////////////////////////////////////////
##/////////////////////////////////////////////////////////////////////////////
##/////////////////////////////////////////////////////////////////////////////

cleanTempFileMapSet() {

# clean up mapset to remove temp files used in classifications
# lower case temp. begin with upper case -> final products

g.mremove -rf rast=^[^A-Z]

}

##/////////////////////////////////////////////////////////////////////////////

export_GeoTiffs() {

#listing of raster maps in current mapset
#MAPS=`g.list type=rast mapset=$MAPSET` ---> regex needed with sed to clean up

#quick implementation -- list dir & append string
#eval `g.gisenv`
#cell=`ls $GISDBASE/$LOCATION_NAME/$MAPSET/cell`
#fcell=`ls $GISDBASE/$LOCATION_NAME/$MAPSET/fcell`
#dcell=`ls $GISDBASE/$LOCATION_NAME/$MAPSET/dcell`
#MAPS="$cell $fcell $dcell"

# listing of mapset rasters that begin with a capitel
CELL=`ls --ignore='[a-z]*' $GISDBASE/$LOCATION_NAME/$MAPSET/cell`
MAPS=$CELL

#echo "maps found are: $MAPS"

for j in $MAPS
do
	#check raster type. cell ->int16 & f/dcell -> float32
	DT=`r.info -t $j | awk -F"=" '{ print $2 }'`
	echo "export data type for $j is $DT"	

	if [ "$DT" = "CELL" ]; then
		TYPE=Int16
	else
		TYPE=Float32
	fi

	r.out.gdal in=$j out=$OUTDIR/geotiffs/"$j".tif type=$TYPE createopt="PROFILE=GeoTIFF,TFW=YES" nodata=-9999
	
done

}

##/////////////////////////////////////////////////////////////////////////////
##/////////////////////////////////////////////////////////////////////////////
### stats/meta-data/variability maps/density plots

derivativeStats() {

##----generate derivative stats----------------------------------------

#listing of rasters for stats. captialized rasters are 'final' outputs
DERV=`ls --ignore="[a-z]*" $GISDBASE/$LOCATION_NAME/$MAPSET/cell`

echo "rasters for stats are: $DERV"

#create array
STAT_ARR=(${DERV//[[:space:]]/ })

for e in "${STAT_ARR[@]}"
do
	r.univar -ge $e | awk -F"=" '{print $2}' | awk -F"\n" 'BEGIN { RS=""; printf "%s\t", "'"$e"'"} {print $1"\t" $2"\t" $3"\t" $4"\t" $5"\t" $6"\t"$7"\t" $8"\t" $9"\t" $10"\t" $11"\t" $12"\t" $13"\t" $14"\t" $15"\t" $16}' >> $CSV_DERV_STATS
done

}

##/////////////////////////////////////////////////////////////////////////////

derviativeMetaData() {

##append to meta data text file

#listing of rasters for stats. captialized rasters are 'final' outputs
DERV=`ls --ignore="[a-z]*" $GISDBASE/$LOCATION_NAME/$MAPSET/cell`

echo "rasters for meta data are: $DERV"

#create array
INFO_ARR=(${DERV//[[:space:]]/ })


# preamble for meta-data file
echo 'Final Raster Meta Data\n\nBased on derviatives in current mapset. Selection based on captialized names\n\n' >>$META_DERV

for e in "${INFO_ARR[@]}"
do
	echo -e "Meta Data for: $e\n" >>$META_DERV	
	r.info -h $e >>$META_DERV
	#echo -e "\n" >>$META_DERV 
	#r.category $e >>$META_DERV
	echo -e "**********************************************************" >>$META_DERV
done

}

##/////////////////////////////////////////////////////////////////////////////

variabilityMaps() {
#variability maps using r.series. output cell values are a function of the input raster values
#calc mean/range/std. grouped by final out prefixes i.e Aspect_/Slope_ AND must be more than 1 occurance of prefix type

echo "calculating variability maps for std/range/mean"

VARIABILITY_LIST=`g.mlist type=rast mapset=$MAPSET exclude=^[a-z]* | sed -e 's/_[0-9]*$//g' | uniq -d`

for i in $VARIABILITY_LIST
do
	
	#echo $i
	#echo `g.mlist type=rast mapset=ip pattern=$i* separator=,`
	r.series -n input=`g.mlist type=rast mapset=$MAPSET pattern=$i* separator=,` output=Variability_$i.std,Variability_$i.range,Variability_$i.avg method=stddev,range,average --overwrite
done

}

##/////////////////////////////////////////////////////////////////////////////

densityPlots() {
##create kernel denisty plots to vis surface form. confined to slope/tcurv/pcurv. if more than
## 1 occurance of prefix type, overlaid on plot.
## kernel density plots are non-parametric & provide better view of dist. histograms are biased by bin size

echo "creating kernel density plots"


DENSITY=`g.mlist -r type=rast mapset=$MAPSET pattern=^[STP]`

#export txt per mapset
for i in $DENSITY
do
	r.stats -1n input=$i output=${OUTDIR}/input_txt_files/density_input_$i.txt
done

##create density plots using R

###needs refactoring & testing with only single input txt

##get listing of density* files
SLOPE=`ls ${OUTDIR}/input_txt_files/density_input_Slope*`
SLOPE_COUNT=`ls ${OUTDIR}/input_txt_files/density_input_Slope* | wc -w`
PCURV=`ls ${OUTDIR}/input_txt_files/density_input_Pcurv*`
PCURV_COUNT=`ls ${OUTDIR}/input_txt_files/density_input_Pcurv* | wc -w`
TCURV=`ls ${OUTDIR}/input_txt_files/density_input_Tcurv*`
TCURV_COUNT=`ls ${OUTDIR}/input_txt_files/density_input_Tcurv* | wc -w`

##=============================================================================
## slope plots

#${OUTDIR}/input_txt_files

SLOPE_OUT1="pdf(file='"`pwd`/$OUTDIR_DENSITY_PLOTS/Slope_density.pdf"')\n"
#SLOPE_OUT4='plot(d1,col="red",xlim=c(0,35), ylim=c(0,0.30), main="Slope Density", xlab="Degrees", ylab="Density")'
#SLOPE_OUT6='legend("topright",c(Args[2],Args[3],Args[4],Args[5]),lty=c(1,1,1,1,1),lwd=c(2.5,2.5,2.5,2.5,2.5),col=c("red", "blue","orange","purple"))'

#counters
c=1
p=0

#create slope array
SLP_ARR=(${SLOPE//[[:space:]]/ })

#create color array
COLOR_ARR=("red" "blue" "black" "orange" "yellow" "green" "brown1" "cyan" "darkblue" "darkgray" "darkviolet" "firebrick" "gold" "pink" "purple" "tan" "plum")

if [ $SLOPE_COUNT -gt 1 ]; then

	echo "slope count is: $SLOPE_COUNT"

	while [ $c -le $SLOPE_COUNT ]
	do
		SLOPE_OUT2=${SLOPE_OUT2}"\ni$c <- scan('"${SLP_ARR[$p]}"')\n"
		SLOPE_OUT3=${SLOPE_OUT3}"\nd$c <- density(i$c)\n"

		#plot()
		if [ $c -eq 1 ]; then
			SLOPE_OUT4="plot(d$c,col='red',xlim=c(0,35), ylim=c(0,0.30), main='Slope Density', xlab='Degrees', ylab='Density')"
		#lines()
		else
			SLOPE_OUT5=${SLOPE_OUT5}"\nlines(d$c, col='"${COLOR_ARR[$p]}"')"
		fi

		#echo $SLOPE_OUT2 $SLOPE_OUT3 $SLOPE_OUT4 $SLOPE_OUT5

		#legend generation for inputs
		SLOPE_LEGEND_ARGS=${SLOPE_LEGEND_ARGS}'"'${SLP_ARR[$p]}'",'
		SLOPE_LEGEND_COLORS=${SLOPE_LEGEND_COLORS}'"'${COLOR_ARR[$p]}'",'

		#increment array
		p=$(( $p + 1 ))

		c=$(( $c + 1 ))
	
	done

	#strip last comma end of SLOPE_LEGEND_ARGS & SLOPE_LEGEND_COLORS
	SLOPE_LEGEND_ARGS=`echo $SLOPE_LEGEND_ARGS | sed -e 's/[,]$//'`
	SLOPE_LEGEND_COLORS=`echo $SLOPE_LEGEND_COLORS | sed -e 's/[,]$//'`

	#assemble legend
	SLOPE_OUT6="legend('"'topright'"',c($SLOPE_LEGEND_ARGS),lty=c(1,1),lwd=c(2.5,2.5),col=c($SLOPE_LEGEND_COLORS))"
	
	echo "legend: $SLOPE_OUT6"

	#assemble final output string
	SLOPE_OUT=${SLOPE_OUT1}${SLOPE_OUT2}${SLOPE_OUT3}${SLOPE_OUT4}${SLOPE_OUT5}'\n'${SLOPE_OUT6}
	#echo "$SLOPE_OUT"
	echo -e $SLOPE_OUT | R --vanilla

else
	#only 1 plot
	for i in $SLOPE
	do	
	SLOPE_OUT="pdf(file='"`pwd`/$OUTDIR_DENSITY_PLOTS/Slope_density.pdf"')\ni1 <- scan('"$i"')\nd1 <- density(i1)\n plot(d1)\nlegend('topright', c('"$i"'),lty=c(1,1),lwd=c(2.5,2.5),col=c('"red"'))"

		echo "R code is: $SLOPE_OUT"
		
		echo -e $SLOPE_OUT | R --vanilla

	done
		
fi

##=============================================================================
## pcurv plots

P_OUT1="pdf(file='"`pwd`/$OUTDIR_DENSITY_PLOTS/Pcurv_density.pdf"')\n"
#P_OUT6='legend("topright",c(Args[2],Args[3],Args[4],Args[5]),lty=c(1,1,1,1,1),lwd=c(2.5,2.5,2.5,2.5,2.5),col=c("red", "blue","orange","purple"))'

#counters
c=1
p=0

#create slope array
P_ARR=(${PCURV//[[:space:]]/ })

#create color array
COLOR_ARR=("red" "blue" "black" "orange" "yellow" "green" "brown1" "cyan" "darkblue" "darkgray" "darkviolet" "firebrick" "gold" "pink" "purple" "tan" "plum")

if [ $PCURV_COUNT -gt 1 ]; then

	echo "pcurv count is: $PCURV_COUNT"

	while [ $c -le $PCURV_COUNT ]
	do

		echo ${P_ARR[$p]}

		P_OUT2=${P_OUT2}"\ni$c <- scan('"${P_ARR[$p]}"')\n"
		P_OUT3=${P_OUT3}"\nd$c <- density(i$c)\n"

		#plot()
		if [ $c -eq 1 ]; then
			P_OUT4="plot(d$c,col='red',xlim=c(-1,1), ylim=c(0,1.0), main='Pcurv Density', xlab='Curv', ylab='Density')"
		#lines()
		else
			P_OUT5=${P_OUT5}"\nlines(d$c, col='"${COLOR_ARR[$p]}"')"
		fi

		echo $P_OUT2 $P_OUT3 $P_OUT4 $P_OUT5

		#legend generation for inputs
		P_LEGEND_ARGS=${P_LEGEND_ARGS}'"'${P_ARR[$p]}'",'
		P_LEGEND_COLORS=${P_LEGEND_COLORS}'"'${COLOR_ARR[$p]}'",'

		#increment array
		p=$(( $p + 1 ))

		c=$(( $c + 1 ))
	
	done

	#strip last comma end of SLOPE_LEGEND_ARGS & SLOPE_LEGEND_COLORS
	P_LEGEND_ARGS=`echo $P_LEGEND_ARGS | sed -e 's/[,]$//'`
	P_LEGEND_COLORS=`echo $P_LEGEND_COLORS | sed -e 's/[,]$//'`

	#assemble legend
	P_OUT6="legend('"'topright'"',c($P_LEGEND_ARGS),lty=c(1,1),lwd=c(2.5,2.5),col=c($P_LEGEND_COLORS))"
	
	echo "legend: $P_OUT6"

	#assemble final output string
	P_OUT=${P_OUT1}${P_OUT2}${P_OUT3}${P_OUT4}${P_OUT5}'\n'${P_OUT6}
	#echo "$SLOPE_OUT"
	echo -e $P_OUT | R --vanilla

else
	#only 1 plot
	for i in $PCURV
	do	
	P_OUT="pdf(file='"`pwd`/$OUTDIR_DENSITY_PLOTS/Pcurv_density.pdf"')\ni1 <- scan('"$i"')\nd1 <- density(i1)\n plot(d1)\nlegend('topright', c('"$i"'),lty=c(1,1),lwd=c(2.5,2.5),col=c('"red"'))"
		
		echo -e $P_OUT | R --vanilla

	done
		
fi

##=============================================================================
## tcurv plots

T_OUT1="pdf(file='"`pwd`/$OUTDIR_DENSITY_PLOTS/Tcurv_density.pdf"')\n"
##T_OUT6='legend("topright",c(Args[2],Args[3],Args[4],Args[5]),lty=c(1,1,1,1,1),lwd=c(2.5,2.5,2.5,2.5,2.5),col=c("red", "blue","orange","purple"))'

#counters
c=1
p=0

#create slope array
T_ARR=(${TCURV//[[:space:]]/ })

#create color array
COLOR_ARR=("red" "blue" "black" "orange" "yellow" "green" "brown1" "cyan" "darkblue" "darkgray" "darkviolet" "firebrick" "gold" "pink" "purple" "tan" "plum")

if [ $TCURV_COUNT -gt 1 ]; then

	echo "tcurv count is: $TCURV_COUNT"

	while [ $c -le $TCURV_COUNT ]
	do

		echo ${T_ARR[$p]}

		T_OUT2=${T_OUT2}"\ni$c <- scan('"${T_ARR[$p]}"')\n"
		T_OUT3=${T_OUT3}"\nd$c <- density(i$c)\n"

		#plot()
		if [ $c -eq 1 ]; then
			T_OUT4="plot(d$c,col='red',xlim=c(-1,1), ylim=c(0,1.0), main='Tcurv Density', xlab='Curv', ylab='Density')"
		#lines()
		else
			T_OUT5=${T_OUT5}"\nlines(d$c, col='"${COLOR_ARR[$p]}"')"
		fi

		echo $T_OUT2 $T_OUT3 $T_OUT4 $T_OUT5

		#legend generation for inputs
		T_LEGEND_ARGS=${T_LEGEND_ARGS}'"'${T_ARR[$p]}'",'
		T_LEGEND_COLORS=${T_LEGEND_COLORS}'"'${COLOR_ARR[$p]}'",'

		#increment array
		p=$(( $p + 1 ))

		c=$(( $c + 1 ))
	
	done

	#strip last comma end of SLOPE_LEGEND_ARGS & SLOPE_LEGEND_COLORS
	T_LEGEND_ARGS=`echo $T_LEGEND_ARGS | sed -e 's/[,]$//'`
	T_LEGEND_COLORS=`echo $T_LEGEND_COLORS | sed -e 's/[,]$//'`

	#assemble legend
	T_OUT6="legend('"'topright'"',c($T_LEGEND_ARGS),lty=c(1,1),lwd=c(2.5,2.5),col=c($T_LEGEND_COLORS))"
	
	echo "legend: $T_OUT6"

	#assemble final output string
	T_OUT=${T_OUT1}${T_OUT2}${T_OUT3}${T_OUT4}${T_OUT5}'\n'${T_OUT6}
	#echo "$SLOPE_OUT"
	echo -e $T_OUT | R --vanilla

else
	#only 1 plot
	for i in $TCURV
	do	
	T_OUT="pdf(file='"`pwd`/$OUTDIR_DENSITY_PLOTS/Tcurv_density.pdf"')\ni1 <- scan('"$i"')\nd1 <- density(i1)\n plot(d1)\nlegend('topright', c('"$i"'),lty=c(1,1),lwd=c(2.5,2.5),col=c('"red"'))"
		
		echo -e $T_OUT | R --vanilla

	done
		
fi

}

##/////////////////////////////////////////////////////////////////////////////

landscape_elevation_shade() {

#produces png output of org elevation overlaid w/org Aspect direction arrows. shows landscape layout for flow

echo "exporting png of elevation hillshade with direction arrows showing aspect"

#create hs z=4
r.shaded.relief map=$2 shadedmap=Elevation_hs_z4_$1 zmult=4 --overwrite

#ensure no instance of png running
d.mon stop=PNG	

#set output name else defaults to map.png
export GRASS_PNGFILE=${OUTDIR}/graphics/landscape_elevation_shades/Landscape_elevation_shade_fdir_arrows_$1.png

#start output of png
d.mon start=PNG

d.his h=$2 i=Elevation_hs_z4_$1

##aspect direction w/arrows
#create magnitude map for d.rast.arrow
r.mapcalc "mag=30"
d.rast.arrow map=Aspect_azimuth_$1 arrow_color="black" grid_color="none" x_color="magenta" skip=50 magnitude_map=mag scale=25

d.text text="$2 hs z=4 Landscape_elevation_shade_fdir_arrows_$1" size=2 color="black" bgcolor="white" align="ll"
d.legend map=$2

d.mon stop=PNG

}

##=============================================================================
##=============================================================================
slope() {
echo "inside slope function"

i=$1

		#slope/aspect/curvature(s)
		r.slope.aspect Elevation_$i slope=Slope_$i aspect=Aspect_org_$i pcurv=Pcurv_$i tcurv=Tcurv_$i min_slp_allow=$MIN_SLOPE_ALLOWED --overwrite
		#convert aspect to azimuth ie. N=0degrees insteade of N=90degrees
		r.mapcalc "Aspect_azimuth_$i = if(isnull(Aspect_org_$i),null() , if((Aspect_org_$i < 90), 90 - Aspect_org_$i, 360+90-Aspect_org_$i))"
		#truncate aspect_azimuth_temp output to int
		r.mapcalc "aspect_azimuth_int_$i = int(Aspect_azimuth_$i)"
		#reclass int degrees to cardinal directions, separated by 90 degrees ie. N=315-45	
		r.reclass input=aspect_azimuth_int_$i output=aspect_azimuth_int_reclass_$i --overwrite < $RECLASS_ASPECT
		#output individual maps for aspect thresholds -- 1=North 2=East 3=South 4=West
			for a in 1 2 3 4
			do
				case $a in
					1) ASPECT_CARDINAL_DIRECTION="North_$i"
						;;
					2) ASPECT_CARDINAL_DIRECTION="East_$i"
						;;
					3) ASPECT_CARDINAL_DIRECTION="South_$i"
						;;
					4) ASPECT_CARDINAL_DIRECTION="West_$i"
						;;
				esac
				r.mapcalc "Aspect_azimuth_$ASPECT_CARDINAL_DIRECTION = (aspect_azimuth_int_reclass_$i == $a)"
			done

		#change default color table for aspect
		r.colors map=Aspect_org_$i color=aspectcolr

		##ensure raster mask applied if appicable to outputs
		r.mapcalc "Slope_$i=Slope_$i"
		r.mapcalc "Aspect_org_$i=Aspect_org_$i"
		r.mapcalc "Pcurv_$i=Pcurv_$i"
		r.mapcalc "Tcurv_$i=Tcurv_$i"
		
		

}

##====

rhpca() {
echo "inside rhpca function"

i=$1

	#rhp-ca -- original contributing area minus catchment area from inverted dem
	#legend: negative values ->ridges, postive ->valley bottoms & 0 -> relative flat areas
	#notes: watershed -a required to compute positive accum. if(x,a,b,c) used to account for negative values\
	#output from subtraction of dems, can not take log of neg value. log10 used to rescale data. 
	#calc accumulation/drainage dir/basins 
	r.watershed -af elevation=Elevation_$i drainage=Drain_mfd_$i accumulation=Accum_mfd_$i --overwrite
	#calc accum for inverted dem --> invert dem = dem *-1
	r.mapcalc "inv_dem_$i = Elevation_$i * -1"
	r.watershed -af elevation=inv_dem_$i drainage=inv_drain_mfd_$i accumulation=inv_accum_mfd_$i --overwrite
	#output unclassified & rescaled using log10 transformation
	r.mapcalc "temp_rhpca_$i = Accum_mfd_$i - inv_accum_mfd_$i"
	r.mapcalc "rhpca_log10_$i = if(temp_rhpca_$i,log(temp_rhpca_$i,10),0,-1*(log(abs(temp_rhpca_$i),10)))"
	#classified into 5 quantile classes -- upper/upper middle/middle/lower middle/lower
	r.quantile -r input=rhpca_log10_$i quantiles=5 | r.recode input=rhpca_log10_$i output=rhpca_log10_recode_$i\
	--overwrite
	r.reclass input=rhpca_log10_recode_$i output=Rhpca_log10_final_$i --overwrite < $RECLASS_RHPCA

}

##====

downslope_index() {
echo "inside downslope_index function"

i=$1

	echo "calculating downslope index"
	downslopeIndex Elevation_$i $i $GIS_OPT_V_DISTANCE
}


##===

twi() {
echo "inside twi function"

i=$1

	r.topidx input=$2 out=Twi_$i --overwrite

	##ensure raster mask applied if appicable to outputs
	r.mapcalc "Twi_$i=Twi_$i"

}

##===

morphological_features() {
echo "inside morphological features function"

i=$1

	r.param.scale input=Elevation_$i output=Morphometric_features_$i param=feature --overwrite

	##ensure raster mask applied if appicable to outputs
	r.mapcalc "Morphometric_features_$i=Morphometric_features_$i"

	##category labels
	echo -e "0:\n1:Planar\n2:Pit\n3:Channel\n4:Pass (saddle)\n5:Ridge\n6:Peak" > ${OUTDIR}/input_txt_files/legend_morphometric_features.txt
	r.category map=Morphometric_features_$i rules=${OUTDIR}/input_txt_files/legend_morphometric_features.txt
}


##===

surface_roughness() {
echo "inside surface roughness function"

	r_roughness $1
}


##=============================================================================
##=============================================================================

##remove any existing mask. may have been set in grass envir prior to executing tool
r.mask -r

##apply water mask if avail
if [ $GIS_FLAG_I = 1 -a "$GIS_OPT_WATER_MASK" != "" ]; then
	# invert the raster mask. raster supplied is not processed. ie) hydrology areas, buildings etc
	echo "inverted mask applied to all raster operations"
	r.mask -i $GIS_OPT_WATER_MASK
elif [ "$GIS_OPT_WATER_MASK" != "" ]; then
	##set supplied mask for all raster operations
	echo "mask applied to all raster operations"	
	r.mask $GIS_OPT_WATER_MASK

	echo "water mask applied is: $GIS_OPT_WATER_MASK"
fi


##main structure to create deriviatives. 

#filter inputs dictate file names inputs/outputs

#loop over filter sizes. must be odd numbered.
for i in $FILTER_ITERATIONS
do
	#compute original raster deriv for baseline stats
	if [ $i != 0 ]; then
		##apply avg filter with mulitple neighborhoods to input raster
		r.neighbors input=$RASTER output=Elevation_$i size=$i method=$FILTER_ITERATIONS_TYPE --overwrite
	else
		echo "calculating orig raster"
		#copy input raster to create required 'Elevation_0' --->future improvement
		g.copy rast=$RASTER,Elevation_$i
		r.mapcalc "Elevation_$i=Elevation_$i"
		#r.neighbors input=$RASTER output=Elevation_$i size=3 method=$FILTER_ITERATIONS_TYPE --overwrite
	
	fi

	
	###----local----------------------------------------------------------- 
	
		##calc slope/aspect/curvature(s) & recode aspect to azimuth ie. N=0degrees insteade of N=90degrees
		##slope/aspect/curvature(s)
		slope $i Elevation_$i

		##pennock orginial 7 classes
		pennock_orginal $i Elevation_$i
	
	###----global (regional) ----------------------------------------------------------
		
		## relative hillslope position using specific catchment area
		rhpca $i Elevation_$i

		##Downslope Index
		## created in SAGA
		downslope_index $i Elevation_$i

		##Elevation Relief Ratio
		##mathmatical similar to hypsometric curve. examines elevation complexity.
		elevation_relief_ratio $i Elevation_$i

	## TWI -- regular
	if [ $GIS_FLAG_T = 1 ]; then
		#TWI -- ln(a/(tanB))
		# very time intensive
		#r.topidx Elevation_$i out=Twi_$i --overwrite
		twi $i Elevation_$i
	fi

	## Morphological Features
	if [ $GIS_FLAG_F = 1 ]; then
		#Morphologic features. Basically Specific points.
		# time intensive
		#r.param.scale input=Elevation_$i output=Morphometric_features_$i param=feature --overwrite
		morphological_features $i Elevation_$i
	fi

	## Surface "Roughness" measures
	if [ $GIS_FLAG_V = 1 ]; then
		## surface roughness -- r.roughness (Add-On script) -- planar/real. examines elevation variance.
		# default settings for spline interp
		#echo "calculating r.roughness"
		#r_roughness $i
		surface_roughness $i
	fi

	###----segmentation----------------------------------------------------
	
	if [ $GIS_FLAG_S = 1 ]; then		
		##Iwahashi/Pike
		#default class set to 8
		iwahashi_pike $i Elevation_$i
		
		##re-enable watermask. IP removes mask at end of function
		##apply water mask if avail
		if [ $GIS_FLAG_I = 1 -a "$GIS_OPT_WATER_MASK" != "" ]; then
			# invert the raster mask. raster supplied is not processed. ie) hydrology areas, buildings etc
			echo "inverted mask applied to all raster operations"
			r.mask -i $GIS_OPT_WATER_MASK
		elif [ "$GIS_OPT_WATER_MASK" != "" ]; then
			##set supplied mask for all raster operations
			echo "mask applied to all raster operations"	
			r.mask $GIS_OPT_WATER_MASK

			echo "water mask applied is: $GIS_OPT_WATER_MASK"
		fi
	

	fi

	if [ $GIS_FLAG_A = 1 ]; then
		##R clustering using Clara & randomForest
		clara_cluster_randomForest $i Elevation_$i	
	fi

	#=====================================================================

	### produces png output of org elevation overlaid w/org Aspect direction arrows. shows landscape layout for flow
	landscape_elevation_shade $i Elevation_$i

done

##=============================================================================

##miscellaneous

#==============================================================================
	


## outputs csv of univar stats for final rasters in mapset (based on capitalized names)
derivativeStats

##format derivative statistics csv file
##post derivative csv stat cleanup -- sort & add header

sort -o $CSV_DERV_STATS $CSV_DERV_STATS | sed -i 1i\ $DERIVATIVE_HEADER $CSV_DERV_STATS

##/////////////////////////////////////////////////////////////////////////////

## outputs meta-data (r.info -h) for final rasters in mapset (based on capitalized names)
derviativeMetaData

###/////////////////////////////////////////////////////////////////////////////

### output pdf plot of kernel density plots from local derviatives -- slope/tcurv/pcurv

densityPlots

###/////////////////////////////////////////////////////////////////////////////

### create variability maps. uses r.series to calc mean/std/range of final rasters. 
##must be more than 1 occurance in series ie Aspect/Slope/IP

variabilityMaps

###/////////////////////////////////////////////////////////////////////////////

### profile plots of input raster. calculated for n/s & e/w orientation. outputs 2 elevation maps with profile line & labels
### uses region bbox for start pts. profile lines spaced according to user input.
### r.profile generates output txts, these are merged by 10 files per new txt. merged files read into R for plots.

### =====================

if [ $GIS_FLAG_Z = 1 ]; then
	##functions

	mergeFiles(){
	##groups output profile txt files into 10 files per new output file for processing in R

	echo "********* inside function $1 $2"

	##http://www.unix.com/shell-programming-scripting/38473-how-merge-files.html  posted 06-06-2007 by user "Shell_Life"
	typeset -i mCnt=0
	typeset -i mSeq=1
	mOutFile="${2}1.txt"
	for mFName in `ls -tr $OUTDIR_PROFILE_PLOTS/tmp/$1*`
	do
	  cat $mFName >> $OUTDIR_PROFILE_PLOTS/tmp/$mOutFile
	  mCnt=$mCnt+1
	  if [ ${mCnt} -eq 10 ]; then
		#calc R plots
		str1='pdf("'"$OUTDIR_PROFILE_PLOTS/Profile_Plots_$2-$mSeq"'.pdf")\ndataset <-read.table("'"$OUTDIR_PROFILE_PLOTS/tmp/$mOutFile"'",na.strings=c("*"))\nplot(dataset$V3,dataset$V4,type="S",main="Profile Plots '"$2-$mSeq"'.txt",xlab="Profile Distance",ylab="Elevation")'  
	
		echo -e $str1 | R -q --vanilla

	    mSeq=$mSeq+1
	    mOutFile=${2}$mSeq".txt"
	    mCnt=0
	  fi
	done

	}

	## ============================================================================
	mkdir $OUTDIR_PROFILE_PLOTS/tmp

	#create hs z=2
	r.shaded.relief map=$RASTER shadedmap=InputRaster_hs_z2 zmult=2 --overwrite

	## ============================================================================

	##create d.graph input file for east-west plots
	EW_P_FILE=profile_ref_map_input_ew.txt
	echo -e "size 1" > $OUTDIR_PROFILE_PLOTS/tmp/$EW_P_FILE

	##create d.graph input file for north-south plots
	NS_P_FILE=profile_ref_map_input_ns.txt
	echo -e "size 1" > $OUTDIR_PROFILE_PLOTS/tmp/$NS_P_FILE

	## ============================================================================

	#extract grass region boundaries into array
	bb=`g.region -t`
	arr=(${bb//// })

	#extents of e/w & n/s --> to determine even # of profiles to construct
	e_ew=$(( ${arr[1]/\.*} - ${arr[0]/\.*} ))
	e_ns=$(( ${arr[3]/\.*} - ${arr[2]/\.*} ))

	#e/w & n/s # profiles from user specificed dist b/w profiles --> not aligned with grid extents
	in=$GIS_OPT_PROFILE_DISTANCE
	p_ew_d=$(( $e_ew / $in ))
	p_ns_d=$(( $e_ns / $in ))

	### construct e/w profiles ====================================================
	i=1
	cumulative=0

	while [ $i -le $p_ns_d ]
	do
		echo "start cumulative is: $cumulative"
		echo "bb start: ${arr[0]/\.*},$(( ${arr[2]/\.*} + $cumulative ))"
		echo "bb end: ${arr[1]/\.*},$(( ${arr[2]/\.*} + $cumulative ))"
	
		##start at southern limit & increment from southern limit by user supplied distance
		r.profile -g input=$RASTER output=$OUTDIR_PROFILE_PLOTS/tmp/profile_ew_$i.txt profile=${arr[0]/\.*},$(( ${arr[2]/\.*} + $cumulative )),${arr[1]/\.*},$(( ${arr[2]/\.*} + $cumulative ))
	
		##append d.graph input file for map showing labeled profiles for ref.
		echo -e "polyline\n${arr[0]/\.*} $(( ${arr[2]/\.*} + $cumulative ))\n${arr[1]/\.*} $(( ${arr[2]/\.*} + $cumulative ))" >> $OUTDIR_PROFILE_PLOTS/tmp/$EW_P_FILE
		#OFF_SET=$(($RANDOM + ($RANDOM % 2) * 32768))
		OFF_SET=$(( $RANDOM / 1000 ))	
		#echo $OFF_SET	
		echo -e "move $(( ${arr[0]/\.*} +  $OFF_SET / 100 )) $(( ${arr[2]/\.*} + $cumulative + 7 ))" >> $OUTDIR_PROFILE_PLOTS/tmp/$EW_P_FILE
		echo -e "text $i" >>$OUTDIR_PROFILE_PLOTS/tmp/$EW_P_FILE


		##increment cumulative distance
		cumulative=$(( $cumulative + $in ))

		##increment counter
		i=$(( $i + 1 ))
		 
	done

	##merge files into groups of 10. created files used for R
	a="profile_ew"
	mergeFiles $a "EW_Profile"

	export GRASS_PNGFILE="$OUTDIR_PROFILE_PLOTS/Profile_Reference_Map_EW.png"
	d.mon start=PNG
	d.his h=$RASTER i=InputRaster_hs_z2
	d.legend $RASTER at=5,8,10,25
	d.graph -m < $OUTDIR_PROFILE_PLOTS/tmp/profile_ref_map_input_ew.txt
	d.mon stop=PNG

	#### construct n/s profiles ====================================================
	i=1
	cumulative=0

	while [ $i -le $p_ew_d ]
	do
		#echo "start cumulative is: $cumulative"
		#echo "bb start: $(( ${arr[0]/\.*} + $cumulative )),${arr[2]/\.*}"
		#echo "bb end: $(( ${arr[0]/\.*} + $cumulative )),${arr[3]/\.*}"
	
		##start at southern limit & increment from southern limit by user supplied distance
		r.profile -g input=$RASTER output=$OUTDIR_PROFILE_PLOTS/tmp/profile_ns_$i.txt profile=$(( ${arr[0]/\.*} + $cumulative )),${arr[2]/\.*},$(( ${arr[0]/\.*} + $cumulative )),${arr[3]/\.*}
	

		##append d.graph input file for map showing labeled profiles for ref.
		echo -e "polyline\n$(( ${arr[0]/\.*} + $cumulative )) ${arr[2]/\.*}\n$(( ${arr[0]/\.*} + $cumulative )) ${arr[3]/\.*}" >> $OUTDIR_PROFILE_PLOTS/tmp/$NS_P_FILE
		#OFF_SET=$(($RANDOM + ($RANDOM % 2) * 32768))
		OFF_SET=$(( $RANDOM / 1000 ))	
		#echo $OFF_SET	
		echo -e "move $(( ${arr[0]/\.*} + $cumulative + 4 )) $(( ${arr[2]/\.*} + $OFF_SET ))" >> $OUTDIR_PROFILE_PLOTS/tmp/$NS_P_FILE
		echo -e "text $i" >> $OUTDIR_PROFILE_PLOTS/tmp/$NS_P_FILE


		##increment ns_cumulative distance
		cumulative=$(( $cumulative + $in ))

		##increment counter
		i=$(( $i + 1 ))
	
	done

	##merge files into groups of 10. created files used for R
	#merge files into groups of 10. created files used for R
	a="profile_ns"
	mergeFiles $a "NS_Profile"


	export GRASS_PNGFILE="$OUTDIR_PROFILE_PLOTS/Profile_Reference_Map_NS.png"
	d.mon start=PNG
	d.his h=$RASTER i=InputRaster_hs_z2
	d.legend $RASTER at=15,18,10,25
	d.graph -m < $OUTDIR_PROFILE_PLOTS/tmp/profile_ref_map_input_ns.txt
	d.mon stop=PNG
fi

###/////////////////////////////////////////////////////////////////////////////

###----export Grass derviatives to ESRI GeoTIFFs--------------------------------

if [ $GIS_FLAG_E = 1 -a $GIS_FLAG_K = 1 ]; then
	#remove temp GRASS rasters
	cleanTempFileMapSet
	export_GeoTiffs
elif [ $GIS_FLAG_E = 1 ]; then
	#export all mapset rasters
	export_GeoTiffs
fi

###/////////////////////////////////////////////////////////////////////////////

###----export PNG rasters of current mapset (d.mon start=PNG---------
### only final rasters exported (determined by captilization using ls --ignore)

if [ $GIS_FLAG_P = 1 ]; then
	## legend & name of raster overlayed. exported as png set at 1600*1200

	## variables
	OUTNAME=0

	#export GRASS enviroments vars
	#eval `g.gisenv`
	
	# listing of mapset rasters that begin with a capitel
	CELL=`ls --ignore='[a-z]*' $GISDBASE/$LOCATION_NAME/$MAPSET/cell`

	LIST=$CELL

	#echo $LIST

	#how many output graphic files. division & mod required. using 4 frames in d.split.frames
	COUNT=`echo $LIST | wc -w`
	
	echo "count of output graphics: $COUNT"

	# grass png driver settings 
	export GRASS_TRUECOLOR=TRUE
	export GRASS_WIDTH=1600
	export GRASS_HEIGHT=1200

	#ensure no instance of png running
	d.mon stop=PNG	

	
	##=============================================================================

	outputGraphics() {
	
	d.mon start=PNG	

		if [ "$1" = "" ]; then
			break
		else
			d.rast.leg $1			
		
			#writes file when stopped			
			d.mon stop=PNG
		fi

	}

	##=============================================================================

	## process outputs

	##load rasters into array from $LIST
	ARR=(${LIST//[[:space:]]/ })

	for c in "${ARR[@]}"
	do
		echo $c
		export GRASS_PNGFILE=$OUTDIR_PNGS/$c.png	
		outputGraphics $c
		
	done

	# close grass monitor
	d.mon stop=PNG
fi

###/////////////////////////////////////////////////////////////////////////////
### remove any raster masks
#echo "attempting to remove any raster MASKs"
r.mask -r

###=============================================================================

##leave with exit status 0 which means "successful"
exit
