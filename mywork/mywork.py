import sys
from datetime import datetime
from pycrown import PyCrown
import argparse
from pathlib import Path

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--chm',
        type=str,
        required=True,
        help='Path to input CHM')

    parser.add_argument(
        '--dsm',
        type=str,
        required=True,
        help='Path to input DSM'
    )

    parser.add_argument(
        '--dem',
        type=str,
        required=True,
        help='Path to input DEM/DTM'
    )

    parser.add_argument(
        '--las_path',
        type=str,
        required=False,
        help='Path to las/z path. Optional: only necessary if you wish to classify your point cloud into individual trees.' \
        'Should be normalized to height above ground.'
    )

    parser.add_argument(
        '--out-dir',
        type=str,
        required=True,
        help='Path to directory where results will be written'
    )

    parser.add_argument(
        '--smooth',
        type=int,
        default=5,
        required=False,
        help='Number of meters to use in CHM smoothing filter. Default = 5.'
    )

    parser.add_argument(
        '--ws_for_tree_detection',
        type=int,
        default=5,
        required=False,
        help='Window size, in meters, used to detect local maxima in tree_detection method. Default = 5.'
    )

    parser.add_argument(
        '--ws_in_pixels',
        type=bool,
        action='store_true',
        required=False,
        help='If given, window size will be evaluated in pixels, not meters. Default = false.'
    )

    parser.add_argument(
        '--min_height',
        type=int,
        required=True,
        help='Minimum height of a tree in meters. Threshold below which a pixel or a point cannot be a local maxima'
    )
    
    parser.add_argument(
        '--cd-algo',
        type=str,
        required=False,
        default='dalponteCIRC_numba',
        help='crown delineation algorithm to be used, choose from: '
        '["dalponte_cython", "dalponte_numba", "dalponteCIRC_numba", "watershed_skimage"].' \
        'Default is dalponteCIRC_numba'
    )

    parser.add_argument(
        '--rem_below',
        type=int,
        required=True,
        help='Used to screen out small trees. In meters. Trees below this height are not evaluated'
    )

    args = parser.parse_args()

    chm_path = Path(args.chm_path)
    if not chm_path.is_absolute():
        chm_path = (Path.cwd() / chm_path).resolve()

    dsm_path = Path(args.dsm_path)
    if not dsm_path.is_absolute():
        dsm_path = (Path.cwd() / dsm_path).resolve()

    dem_path = Path(args.dem_path)
    if not dem_path.is_absolute():
        dem_path = (Path.cwd() / dem_path).resolve()

    laz_path = Path(args.las_path)
    if not laz_path.is_absolute():
        laz_path = (Path.cwd() / laz_path).resolve()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()

    chm_smoothby = args.smooth
    window_size = args.ws_for_tree_detection
    # ask: can i assume that if someone wants to use ws_in_pixels=True for filter_chm, they
    # also want to use that option for tree_detection? or nah
    ws_in_pixels = args.ws_in_pixels
    hmin = args.hmin
    cd_algo = args.cd_algo
    treetop_min = args.rem_below

    timer_start = datetime.now()

    # set input files -- all are strings containing the path to the data file

    # DEL: chm_path = "data/my_chm.tif"
    # DEL: dem_path = "data/my_dem.tif" # path to digital terrain model 
    # DEL: dsm_path = "data/my_dsm.tif" # path to digital surface model
    # DEL: las_path = "data/my_las.las" # path to las file --> only needed if you wish to classify the point cloud into individual trees 

    # initialize an instance/object of the PyCrown class
    pc = PyCrown(chm_path, dem_path, dsm_path, laz_path, outpath=out_dir)

    # smooth CHM with a median filter, num meters is 5 by default but can be edited via command line args
    pc.filter_chm(chm_smoothby, ws_in_pixels=ws_in_pixels)

    # tree detection with local maxima filter
    pc.tree_detection(pc.chm, window_size, ws_in_pixels=ws_in_pixels, hmin=hmin)

    # clip trees to bounding box (ASK -- done in preprocessing right?)
    pc.clip_trees_to_bbox(inbuf=11) # ASK -- do we want 11?
    # ASK -- do we want to do this step even? do we do the clipping in the preprocessing step?

    # crown delineation
    pc.crown_delineation(algorithm=cd_algo, th_tree=15.,
                         th_seed=0.7, th_crown=0.55, max_crown=10.)
        # ASK abt vales for th_tree, th_seed, th_crown, max_crown

    # correct tree tops on steep terrain -- optional
    pc.correct_tree_tops()

    # calculate tree height and elevation
    pc.get_tree_height_elevation(loc='top') # top - initial
    pc.get_tree_height_elevation(loc='top_cor') # top_cor - corrected

    # screen small trees: 
        # removes small trees based on minimum
        # tree dataframe and crown raster is updated
    pc.screen_small_trees(hmin=treetop_min, loc='top')
    # ASK - how is this hmin different from the one used above??? 

    # convert raster crowns to polygons
    pc.crowns_to_polys_raster()
    pc.crowns_to_polys_smooth(store_las=True)
    # ASK ^^ store_las should be true if point clouds should be classified and stored externally -- should they? 

    # check that all geometries are valid
    pc.quality_control()

    # export results
    pc.export_raster(pc.chm, pc.outpath / '_chm.tif', 'CHM')
    pc.export_tree_locations(loc='top')
    pc.export_tree_locations(loc='top_cor')
    pc.export_tree_crowns(crowntype='crown_poly_raster')
    pc.export_tree_crowns(crowntype='crown_poly_smooth')

    timer_end = datetime.now()

    print(f"Number of trees detected: {len(pc.trees)}")
    print(f"Processing time: {timer_end - timer_start} [HH:MM:SS]")
