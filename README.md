
# PyCrown - A Flexible Adaptation
* Original PyCrown module by Dr. Jan Schindler
* Adaptation by Ava Romano (<mailto:ajromano@calpoly.edu>), advised by Michael Huggins

Published under GNU GPLv3


# Summary
The purpose of this repo is to document the work done on my individual project for GEOG 441, Advanced Geospatial Applications, at California Polytechnic State University. This has involved two main undertakings: development of a Python-PDAL script to generate a CHM, DEM, DSM, and hag-normalized las file, and a flexible version of the open-source PyCrown script authored by Dr. Jan Schindler. 

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

# Flexible PyCrown Adaptation
My goal with this adaptation was to create a singular PyCrown script that takes data sources and method parameters as command line arguments so that it can be repeatedly run from the command-line without need for back-and-forth editing. 

### Note:
This part of the repo is to document my work up to this point.

However, this segment of the project is not finished. Running flexy_pc.py as it current sits in this repo will produce errors. 

I am actively working through debugging it, and adding extra options to increase customization and adaptability. 

### On my goals and background as they relate to this project: 
**My overall goal** is to create a PyCrown script that the user need not edit (or need not edit extensively) to be useful to them. My way of achieving this thus far has been to carefully read the methods that make up pycrown.py, understand what arguments they take (or can take), and do my best to assess what arguments are important to allow the user to customize.

*As a disclaimer*, I am an undergraduate student, and this is my first time working with tree crown delineation and segmentation. It is entirely possible that I might make an oversight regarding what parameters are important to include as command-line arguments and which are not. 

That being said -- If you come across this project and have an idea you feel could improve it, please reach out. 
My goal is to make this script as flexible and useful to as many people as possible, and that includes garnering inputs from many sources. External recommendations are always welcome.

## My script and how it differs
The original PyCrown script which mine is based on is still in this repo, under *example/example.py*. 

My adaptation can be found in *mywork/flexy_pc.py*.

### Main changes made
* Adding command-line arguments for data sources and certain method parameters
* More to come!

## Using flexy_pc.py
Follow the "installation and environment setup" steps given in the [original PyCrown module](<https://github.com/manaakiwhenua/pycrown>). In your PyCrown environment, run the tests, install the PyCrown module, run the example.py script, and compare your results to those in the original Git repo to ensure that the original PyCrown module works on your system.

### The script flexy_pc.py can by run with the below arguments.

## Arguments to flexy_pc.py
**--chm:** Path to input CHM. Can be relative or absolute. Type=str. \[Required\]

**--dsm:** Path to input DSM. Can be relative or absolute. Type=str. \[Required\]

**--dem:** Path to input DEM/DTM. Can be relative or absolute. Type=str. \[Required\]

**--las_path:** Path to input las/z. Can be relative or absolute. Only necessary if you wish to classify your point cloud into individual trees and store it externally. Giving a las_path with set the store_las parameter of "the crowns_to_polys_smooth" method to True. Point cloud should be normalized to height above ground -- this can be done with the attached preprocessing script. Type=str. \[Optional\]

**--out_dir:** Path to directory where results (tree top locations .shp, tree crowns .shp, optional tree-classified .las file) will be stored. Can be relative or absolute. Type=str. \[Required\]

**--smooth:** Specifies the number of units to use in CHM smoothing filter. If --ws-in-pixels is passed, this int will be evaluated as a number of pixels. Otherwise, this number will be in the units of your CHM. However, the default value is as such because meters are the assumed unit. You should set this to be larger if you are working in feet. Default=5. Type=int. \[Optional\]

**--ws_for_tree_detection:** Window size used to detect local maxima in the tree_detection method. Will be interpreted as the units your CHM is in unless --ws_in_pixels is given. Default=5. Type=int. \[Optional\]

**--ws_in_pixels:** If given, window size will be evaluated in pixels, not units, for both the . Units depend on whatever your CHM is. Default = false. Type=int. \[Optional\].

**--hmin:** Minimum height of a tree in CHM units. Threshold below which a pixel or a point cannot be a local maxima. Default is as such because meters are the assumed unit. You should set this to be larger if you are working in feet. Default=5. Type=int. \[Optional\].'
* *Note*: The same hmin is taken to be used for the tree_detection method and the screen_small_trees method, but for the former, it is passed as 'hmin+2' because it was not clear to us what exactly screen_small_trees does if tree_detection has an hmin parameter -- we are still looking into it, and it will probably change.

**--cd_algo:** Crown delineation algorithm to be used, choose from: "dalponte_cython", "dalponte_numba", "dalponteCIRC_numba", "watershed_skimage". Default is dalponteCIRC_numba. Type=str. \[Optional\].

**Notes:**
* In the *clip_trees_to_bbox* method, inbuf is hardcoded to 1. This is because we tried testing by not passing any parameters to this method, and the "No clipping method" error was thrown. To temporarily remediate this, I hardcoded inbuf to 1. It might be that this method is not necessary unless clipping is required, and I can take it out altogther. Ie, it's in progress. 
* In the *filter_chm* method, window size is currently hardcoded to 1 for testing purposes. It seems that this method only works if the window_size number matches the raster's resolution. We are also experiencing some data type issues which may be occurring because of our raster resolutions. Ie, also in progress.
* My code is thoroughly commented at the moment, mostly with notes to myself. It is not difficult to read, but there is a lot of extra fluff in there at the moment. This is temporary, and will change as I make progress and update this repo.

## Current bug:
*"TypeError: No matching definition for argument type(s) array(float64, 2d, C), array(int32, 2d, C), float64, float64, float64, float64"*. Believed this issue comes from Numba. Working to interpret this issue and what must be done to avoid it. 

# Looking ahead
As I continue to develop this project over the coming weeks/months, my focuses will be: 

* Getting my pycrown-adapted script (*flexy_pc.py*) to actually work
* Understanding the methods available in the PyCrown object, which to include in my script, and what of their parameters are important to make optional on the command line
* Creation of a docker file to containerize my development environments and make them even more portable and widely reusable --> Potentially utilize quay.io, and also Git Action to connect to quay.io
* (Far ahead) Possibley even update PyCrown to newer Python versions

# Final notes
Many thanks to Dr. Jan Schindler for producing the entire code base that this project is built on, and to Prof. Michael Huggins at Cal Poly for constant guidance and advice regarding this project. 