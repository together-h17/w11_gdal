# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:50:11 2024

@author: AE133
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:32:14 2024

@author: AD200
"""

import geopandas as gpd
from osgeo import gdal
from shapely.geometry import Polygon

polygon_path = r'C:\Users\AE133\Desktop\SG42\圖資\農田網格_all(-).shp'
tif_path = r'C:\Users\AE133\Desktop\SG42\MyProject\tin_yl_tinra.tif'
output_path = polygon_path.replace('.shp', '_DSM.shp')

ds = gdal.Open(tif_path)
gt_forward = ds.GetGeoTransform() #獲取轉換參數(檔頭那些)
gt_reverse = gdal.InvGeoTransform(gt_forward) #將地理坐標轉換回像素坐標
raster_band = ds.GetRasterBand(1)

polygons = gpd.read_file(polygon_path, encoding = 'utf-8')
output_dict = dict()
count = 0

for index, row in polygons.iterrows():
    new_polygon = []
    
    #讀polygon中心點轉換成像素座標的值
    centroid = row['geometry'].centroid
    px, py = gdal.ApplyGeoTransform(gt_reverse, centroid.x, centroid.y)
    
    # 從光柵中讀取該像素位置的高程值
    intval = raster_band.ReadAsArray(px, py, 1, 1)
    z = 0
    if intval:
        z = intval[0][0]
        
    
    new_row = row.copy()
    new_row['z'] = z
    
    output_dict[count] = new_row
    count += 1

output = gpd.GeoDataFrame.from_dict(output_dict, orient = 'index')
output.crs = polygons.crs
output.to_file(output_path, encoding = 'utf-8', driver = 'ESRI Shapefile', 
               engine = 'pyogrio')
