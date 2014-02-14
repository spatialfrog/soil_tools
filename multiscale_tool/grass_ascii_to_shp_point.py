"""
converts grass gis v.out.ascii text files for slope length calculation to point shapefiles.

ref:
http://www.macwright.org/2012/10/31/gis-with-python-shapely-fiona.html
"""

import csv
import argparse
import os
from shapely.geometry import Point, mapping
from fiona import collection

# input cli arguments
description="""run csv_to_point.py --input_ascii peak.txt --iteration 0 --out_dir ."""
cli_args=argparse.ArgumentParser(description=description)
cli_args.add_argument("--input_ascii",help="full path to grass ascii file.")
cli_args.add_argument("--iteration",help="spatial filter iteration number.")
cli_args.add_argument("--out_dir",help="output directory for shapefile.")

args=cli_args.parse_args()

# output shapefile will have same name as input csv file with spatial filter iteration number
csv_name=os.path.splitext(os.path.basename(args.input_ascii))[0]
out_shapefile_name=os.path.join(args.out_dir,csv_name + "_" + args.iteration + ".shp")

schema = { 'geometry': 'Point', 'properties': { 'id': 'str' } }
with collection(
    out_shapefile_name, "w", "ESRI Shapefile", schema) as output:
    with open(args.input_ascii, 'rb') as f:
        reader = csv.DictReader(f,fieldnames=["X","Y","Z"])
        for row in reader:
            point = Point(float(row['X']), float(row['Y']))
            output.write({
                'properties': {
                    'id': row['Z']
                },
                'geometry': mapping(point)
            })
