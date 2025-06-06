import sys
from datetime import datetime
from pycrown import PyCrown
import argparse
from pathlib import Path

""" 

    Required args: 
        --chm: path to input CHM.
        --dsm: path to input DSM.
        --dem: path to input DEM.
        --out_dir: path to output directory.
    Optional args:
        --las_path: path to las/z if classifying point cloud by individual trees.
        --smooth: num units (or pixels) to use in CHM median smoothing filter. Def = 3.
        --ws_for_tree_detection: window size for tree detection. Def = 5.
        --ws_in_pixels: determines if --ws_for_tree_detection will be in units or pixels. Def = false.
        --hmin: height below which a point cannot be considered a local maxima (ie a tree). Def = 5.
        --cd-algo: determines which crown detection algo to use. Default is recommended.

"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--chm',
        type=str,
        required=True,
        help='Path to input CHM. Type=str. [Required]')

    parser.add_argument(
        '--dsm',
        type=str,
        required=True,
        help='Path to input DSM. Type=str. [Required]'
    )

    parser.add_argument(
        '--dem',
        type=str,
        required=True,
        help='Path to input DEM/DTM. Type=str. [Required]'
    )

    parser.add_argument(
        '--las_path',
        type=str,
        required=False,
        help='Optional. Path to las/z input file. Only necessary if you wish to classify your point cloud into individual trees'
        'and store it externally. Giving a las_path with set the store_las parameter of "the crowns_to_polys_smooth" method to True.' \
        'Point cloud should be normalized to height above ground -- this can be done with the attached preprocessing script. Type=str. [Optional].'
    )

    parser.add_argument(
        '--out_dir',
        type=str,
        required=True,
        help='Path to directory where results will be written. Type=str. [Required]'
    )

    parser.add_argument(
        '--smooth',
        type=int,
        default=5,
        required=False,
        help='Number of units to use in CHM smoothing filter. If --ws-in-pixels is passed, this int will ' \
        'be evaluated as a number of pixels. Otherwise, this number will be in the units of your CHM.' \
        'Default is as such because meters are the assumed unit. You should set this to be larger if you are working in feet. ' \
        'Default=5. Type=int. [Optional]'
    )

    parser.add_argument(
        '--ws_for_tree_detection',
        type=int,
        default=5,
        required=False,
        help='Window size used to detect local maxima in tree_detection method. ' \
        'Will be interpreted as the units your CHM is in unless --ws_in_pixels is given.' \
        'Default=5. Type=int. [Optional].'
    )

    parser.add_argument(
        '--ws_in_pixels',
        action='store_true',
        required=False,
        help='If given, window size will be evaluated in pixels, not units. Units depend on whatever your CHM is. Default = false.' \
        'Type=int. [Optional].'
    )

    parser.add_argument(
        '--hmin',
        type=int,
        required=False,
        default=5,
        help='Minimum height of a tree in CHM units. Threshold below which a pixel or a point cannot be a local maxima.' \
        'Default is as such because meters are the assumed unit. You should set this to be larger if you are working in feet.' \
        'Default=5. Type=int. [Optional].'
    )
    
    parser.add_argument(
        '--cd_algo',
        type=str,
        required=False,
        default='dalponteCIRC_numba',
        help='Crown delineation algorithm to be used, choose from: '
        '["dalponte_cython", "dalponte_numba", "dalponteCIRC_numba", "watershed_skimage"].' \
        'Default is dalponteCIRC_numba. Type=str. [Optional].'
    )

    args = parser.parse_args()

    chm_path = Path(args.chm)
    if not chm_path.is_absolute():
        chm_path = (Path.cwd() / chm_path).resolve()

    dsm_path = Path(args.dsm)
    if not dsm_path.is_absolute():
        dsm_path = (Path.cwd() / dsm_path).resolve()

    dem_path = Path(args.dem)
    if not dem_path.is_absolute():
        dem_path = (Path.cwd() / dem_path).resolve()

    if args.las_path:
        laz_path = Path(args.las_path)
        if not laz_path.is_absolute():
            laz_path = (Path.cwd() / laz_path).resolve()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()

    chm_smoothby = args.smooth
    window_size = args.ws_for_tree_detection
    ws_in_pixels = args.ws_in_pixels
    hmin = args.hmin
    cd_algo = args.cd_algo
    timer_start = datetime.now()

    # initialize an instance/object of the PyCrown class
    if args.las_path:
        pc = PyCrown(chm_path, dem_path, dsm_path, laz_path, outpath=out_dir)
    else:
        pc = PyCrown(chm_path, dem_path, dsm_path, outpath=out_dir)

    # smooth CHM with a median filter, num meters is 5 by default but can be edited via command line args
    # 1 is hardcoded for testing purposes -- it seems that this only works if this int matches the raster's resolution, and 
    # some data type issues have been raised by this, and by the resolution of the .tifs i am currently working with.
    # tldr: under construction
    pc.filter_chm(1, ws_in_pixels=True)

    # tree detection with local maxima filter
    pc.tree_detection(pc.chm, window_size, ws_in_pixels=ws_in_pixels, hmin=hmin+2) # explain why u did the plus 2 in docs 

    # clip trees to bounding box (ASK -- done in preprocessing right?)
    pc.clip_trees_to_bbox(inbuf=1) # DOCS: all args are optional, but if you dont give one of: bbox, inbuf, or f_tiles, a "no clipping method specified" error will be thrown
    # ASK -- do we want to do this step even? do we do the clipping in the preprocessing step?

    # crown delineation
    pc.crown_delineation(algorithm=cd_algo, th_tree=2.,
                         th_seed=0.7, th_crown=0.55, max_crown=10.)
        # ASK abt values for th_tree, th_seed, th_crown, max_crown -- check r docs and read paper 

    # correct tree tops on steep terrain -- optional
    pc.correct_tree_tops()

    # calculate tree height and elevation
    pc.get_tree_height_elevation(loc='top') # top - initial
    pc.get_tree_height_elevation(loc='top_cor') # top_cor - corrected

    # screen small trees: 
        # removes small trees based on minimum
        # tree dataframe and crown raster is updated
    pc.screen_small_trees(hmin=hmin, loc='top')
    # ASK - how is this hmin different from the one used above??? 

    # convert raster crowns to polygons
    pc.crowns_to_polys_raster()
    if laz_path: 
        pc.crowns_to_polys_smooth(store_las=True)
    else:
        pc.crowns_to_polys_smooth(store_las=False)
    
    # check that all geometries are valid
    pc.quality_control()

    # export results
    pc.export_raster(pc.chm, pc.outpath / '_pc_chm.tif', 'CHM')
    pc.export_tree_locations(loc='top')
    pc.export_tree_locations(loc='top_cor')
    pc.export_tree_crowns(crowntype='crown_poly_raster')
    pc.export_tree_crowns(crowntype='crown_poly_smooth')

    timer_end = datetime.now()

    print(f"Number of trees detected: {len(pc.trees)}")
    print(f"Processing time: {timer_end - timer_start} [HH:MM:SS]")
