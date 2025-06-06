[![manaakiwhenua-standards](https://github.com/manaakiwhenua/pycrown/workflows/manaakiwhenua-standards/badge.svg)](https://github.com/manaakiwhenua/manaakiwhenua-standards)


# PyCrown - A Flexible Adaptation
* Original PyCrown code by Dr. Jan Schindler
* Adaptation by Ava Romano (<mailto:ajromano@calpoly.edu>)

Published under GNU GPLv3


# Summary
The purpose of this repo is to document the work done on my individual project for GEOG 441, Advanced Geospatial Applications, at Cal Poly. This has involved two main undertakings: development of a Python-PDAL script to generate a CHM, DEM, DSM, and hag-normalized las file, and a flexible version of the open-source PyCrown script authored by Dr. Jan Schindler. 

This repo is not intended to provide a in-depth description of PyCrown. For that purpose, please see the original PyCrown repo (<https://github.com/manaakiwhenua/pycrown>).

# Preprocessing
PyCrown requires a CHM, DEM/DTM, and DSM. In the *"mywork"* folder, you will find preprocessing.py. This is a Python script whose essential function is to take in a point cloud and output a CHM, DEM, and DSM. It does this by running the las file through a Python-PDAL pipeline. It also provides the option to clip the las file's extent to that defined by a geojson. It will also write a new las file with heights normalized to height above ground.

# Using preprocessing.py
**Note:** It is important that preprocessing.py and flexy_pc.py are run in different environments, because the latter operates in Python 3.6, and the former in 3.13.3.
## Creating the preprocessing environment
An environment file, `preprocess_env.yml`, is provided in the *mywork* folder for this purpose.

I have only used conda environments to run this script, but you are welcome to use any environment method you prefer.

### To create an environment in conda with the provided .yml
`conda env create -f preprocess_env.yml`

## Arguments to preprocessing.py
**--las_path:** Path to input las/z file. Can be relative or absolute. Type=str. \[Required\]

**--out_dir:** Path to directory where results (CHM, DEM, DSM, (optional) normalized point cloud) will be written. Can be relative or absolute. Type=str. \[Required\]

**--clip:** Specifies that you would like your las file to be clipped to the extent of a given geojson. If you give this argument, you must also give a geojson with the --geojson argument. You must either give --clip or --no-clip (but not both). 

**--no-clip:** Specifies that you would not like to clip your las file. You must either give --clip or --no-clip (but not both).

**--geojson:** Use only if you passed --clip. Path to a geojson to be used for clipping your las file. CRS must exactly match the CRS of your las file. Path can be relative or absolute. Type=str. \[Optional\]

**–ws_dsm:** Specifies the *window_size* argument to be used for the PDAL Writers.gdal stage that generates the DSM. Default=1. Type=int. \[Optional\]

**–ws_dem:** Specifies the *window_size* argument to be used for the PDAL Writers.gdal stage that generates the DEM. We found this number often needed to be larger than other window size args, so its default value is bigger. Default=5. Type=int. \[Optional\]

**–ws_chm:** Specifies the *window_size* argument to be used for the PDAL Writers.gdal stage that generates the CHM. Default=1. Type=int. \[Optional\]

### Note: 
In all Writers.gdal stages, resolution is hardcoded to 0.3, and meters are the assumed unit.

## To use this script in a terminal (with your environment activated)
`python preprocessing.py --las_path *path/to/las/* --out_dir *path/to/directory/* --clip --geojson *path/to/geojson/*`