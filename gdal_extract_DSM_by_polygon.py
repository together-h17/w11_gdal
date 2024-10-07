# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:32:14 2024

@author: AD200
"""

import geopandas as gpd
from osgeo import gdal
from shapely.geometry import Polygon

polygon_path = r'P:\13018-113年及114年三維道路模型建置案\04_小組會議\SG42\Plane Fitting\2.法二\刪好\苗栗\苗栗刪好.shp'
tif_path = r'P:\13018-113年及114年三維道路模型建置案\04_小組會議\SG42\Plane Fitting\DSM\Miaoli\Miaoli_02_LOD2_0.5DSM_DSM_merge.tif'
output_path = polygon_path.replace('.shp', '_DSM.shp')

ds = gdal.Open(tif_path)
gt_forward = ds.GetGeoTransform()
gt_reverse = gdal.InvGeoTransform(gt_forward)
raster_band = ds.GetRasterBand(1)

polygons = gpd.read_file(polygon_path, encoding = 'utf-8')
output_dict = dict()
count = 0

for index, row in polygons.iterrows():
    new_polygon = []
    for xyz in row['geometry'].exterior.coords:
        px, py = gdal.ApplyGeoTransform(gt_reverse, xyz[0], xyz[1])
        intval = raster_band.ReadAsArray(px, py, 1, 1)
        z = 0
        if intval:
            z = intval[0][0]
        new_polygon.append((xyz[0], xyz[1], z))
    
    new_row = row.copy()
    new_row['geometry'] = Polygon(new_polygon)
    
    output_dict[count] = new_row
    count += 1

output = gpd.GeoDataFrame.from_dict(output_dict, orient = 'index')
output.crs = polygons.crs
output.to_file(output_path, encoding = 'utf-8', driver = 'ESRI Shapefile', 
               engine = 'pyogrio')
