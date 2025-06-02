# run in a separate environment to pycrown environment -- have pdal, python-pdal, geopandas 

# tell user: 
    # 1. if they are using this preprocessing script to clip a tile, they must
    # input a geojson as their bbox, and it must be the same crs as the tile
    # 2. required CL args: path to .las file
    # 3. resolution is hardcoded to 0.3 #dealwithit
    # 4. window_size default is 1, there is an optional CL arg for it 

#%%
import sys
import argparse 
import pdal
from pathlib import Path
import geopandas as gpd

#%% 
parser = argparse.ArgumentParser()

parser.add_argument(
    '--las_path',
    type=str,
    required=True,
    help='Path to input las/z file')

parser.add_argument(
    '--out_dir',
    type=str,
    required=True,
    help='Path to directory where results (CHM, DSM, DEM, normalized las) will be written'
)

parser.add_argument(
    '--clip',
    type=bool,
    action=argparse.BooleanOptionalAction,
    required=True,
    help='Whether or not you would like the preprocessing script to clip your las data to a smaller extent.' \
    'If you would, do: "--clip" with "--geojson" and include your geojson (in the same crs as your las data) which delineates your target extent.' \
    'If not, do: --no-clip.'
)

parser.add_argument(
    '--geojson',
    type=str,
    required=False,
    help='Optional path to a geojson, if you would like to clip your las data to a smaller extent.' \
    'Only pass in if --clip is marked as True. geojson and las crs must match exactly.'
)

parser.add_argument(
    '--window_size',
    type=int,
    default=1,
    required=False,
    help='window_size argument to be used for the PDAL Writers.gdal stage. Default is 1.'
)

args = parser.parse_args()

laz_path = Path(args.las_path)
if not laz_path.is_absolute():
    laz_path = (Path.cwd() / laz_path).resolve()

out_dir = Path(args.out_dir)
if not out_dir.is_absolute():
    out_dir = (Path.cwd() / out_dir).resolve()

gdf_path = Path(args.geojson)
if not gdf_path.is_absolute():
    gdf_path = (Path.cwd() / gdf_path).resolve()

window_size = args.window_size


#%%

# laz_path = Path('/Users/avaromano/441/441indivproj/mywork/data/USGS_LPC_CA_CarrHirzDeltaFires_2019_B19_10TDL0465045112.laz')

# create CHM, DSM, DEM, DTM output paths
#out_dir = Path("/Users/avaromano/441/441indivproj/mywork/result")
print(out_dir)
stem = laz_path.stem
chm_path = out_dir/(f"{stem}_chm.tif")
dsm_path = out_dir/(f"{stem}_dsm.tif")
dem_path = out_dir/(f"{stem}_dem.tif")

# create an instance of the pipeline object
pipeline = pdal.Reader.las(filename=laz_path).pipeline()

# 0: filter noise
classify_low_noise = pdal.Filter.elm() # ASK if need args = maybe if there's time
classify_outlier = pdal.Filter.outlier() # ASK if need args = maybe via command line if time --> make as flexible as possible 
filter_noise = pdal.Filter.expression(expression="Classification != 7")
# 1: make polygon in Q, get layer extent, export as geojson/geopkg/shp, add column

#%% 
# QUESTION 2: do we want to make this step optional?
# QUESTION 3: why didn't the relative path work for gpd.read_file? 
# TODO: take file name as command line arg
if args.clip and not args.geojson:
    sys.exit("No geojson given to clip with")

if args.clip and args.geojson:
    gdf = gpd.read_file(str(gdf_path))
    gdf['val'] = 99
    gdf.to_file(str(gdf_path))

    # step 2: create new dimension in point cloud
    create_dimension = pdal.Filter.assign(value="val = 0") 

    # step 3: assign val = 99 to points in point cloud that are within box
    assign_dimension = pdal.Filter.overlay(dimension="val",
                                       datasource=str(gdf_path),
                                       column="val"
                                       )

    # step 4: select points where val = 99 (which are points within bbox)
    select_points_in_bbox = pdal.Filter.expression(expression="val == 99")
#%% 
""" gdf_path = Path("/Users/avaromano/441/441indivproj/mywork/data/little_poly.geojson")
gdf = gpd.read_file(str(gdf_path))
gdf['val'] = 99
gdf.to_file(str(gdf_path))

create_dimension = pdal.Filter.assign(value="val = 0") 
assign_dimension = pdal.Filter.overlay(dimension="val",
                                       datasource=str(gdf_path),
                                       column="val"
                                       )
select_points_in_bbox = pdal.Filter.expression(expression="val == 99") """

# step 5: normalize to height above ground
height_above_ground = pdal.Filter.hag_nn(count=2)

# step 6: make DSM
make_DSM = pdal.Writer.gdal(
    filename=dsm_path,
    output_type="max",
    window_size=window_size,
    resolution=0.3
    )

# step 7: make DEM
make_DEM = pdal.Writer.gdal(
    filename=dem_path, 
    output_type="min",
    resolution=0.3,
    window_size=window_size,
    where="(Classification == 2) && (ReturnNumber == NumberOfReturns)"
    )

# step 8: copy points from hag to z
make_z_hag = pdal.Filter.ferry(
    dimensions="HeightAboveGround=>Z"
    )

# step 9: make CHM
make_CHM = pdal.Writer.gdal(
    filename=chm_path,
    resolution=0.3,
    window_size=window_size,
    output_type="max",
    where="ReturnNumber == 1" 
)
#%%
# step 10: write to las
output_las = out_dir/(f"{stem}_processed.laz")
write_to_las = pdal.Writer.las(filename=output_las) # ASK -- want any other args? 
# 11: append to pipeline
# put on diff lines and specfy to add if not none 
pipeline |= classify_low_noise | classify_outlier | filter_noise 
pipeline |= create_dimension | assign_dimension | select_points_in_bbox 
pipeline |= height_above_ground
pipeline |= make_DSM | make_DEM | make_z_hag | make_CHM 

pipeline.execute()
