# -*- coding:utf-8 -*-
__auther__ = 'Henning'
# Python Version : win_X64 3.6.6
# Time : 2018-08-13-8:26
# Desc : csv转shapefile。使用osgeo的gadal对shapefile进行操作
'''
gdal的whl文件下载地址：https://www.lfd.uci.edu/~gohlke/pythonlibs/ 
'''

import os
import csv
from osgeo import ogr, osr, gdal


def csv2shp(csv_path, shp_path):
    # shapefile字段长度不能太长，字段最长为10
    field_names = ["Rover_id", "Ip_address", "data", "Mounppint", "Servise", "Mounppint2", "User", "Start_date",
                   "Start_time", "Over_date", "Over_time", "Distance", "Bytes_sent", "Lat", "Lon", "Elevation"]

    # 设置相关属性，坐标系、驱动、中文
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  # 路径中文
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 属性中文
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(shp_path)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # 创建点图层和字段名称
    layer = data_source.CreateLayer("point", srs, ogr.wkbPoint)
    for field_name in field_names:
        # field = ogr.FieldDefn(field_name, ogr.OFTString)  # ogr.OFTString -> shapefile String
        # field.SetWidth(50)  # 设置长度
        # layer.CreateField(field)  # 创建字段
        layer.CreateField(ogr.FieldDefn(field_name, ogr.OFTString))

    # 打开CSV文件 并逐行遍历
    csv_file = csv.reader(open(csv_path, 'r'))
    # csv_reader = csv.DictReader(open(csv_path, 'r'))
    try:
        for line_info in csv_file:
            try:
                if len(line_info[13]) < 2 or len(line_info[14]) < 2:
                    continue
                # 获取每一行的经纬度信息
                lon = line_info[14]
                lat = line_info[13]
                lon_du = lon[:lon.find("°")]
                lon_fen = lon[lon.find("°") + 1:lon.find("'")]
                lon_miao = lon[lon.find("'") + 1:lon.find('"')]
                lat_du = lat[:lat.find("°")]
                lat_fen = lat[lat.find("°") + 1:lat.find("'")]
                lat_miao = lat[lat.find("'") + 1:lat.find('"')]
                lon = float(lon_du) + float(lon_fen) / 60 + float(lon_miao) / 3600
                lat = float(lat_du) + float(lat_fen) / 60 + float(lat_miao) / 3600
            except ValueError as e:
                print(e)
                print("坐标处理错误！请检查坐标数据。" + csv_path)
                continue
            except IndexError as e:
                print(e)
                print("索引异常：" + csv_path)
                continue
            except Exception as e:
                print(e)
                print(csv_path)
                continue

            # 创建点Feature，并设置geometry
            point_feature = ogr.Feature(layer.GetLayerDefn())
            wkt = "POINT(%f %f)" % (lon, lat)
            point = ogr.CreateGeometryFromWkt(wkt)
            point_feature.SetGeometry(point)

            # 根据字段内容设置属性值
            for i in range(len(field_names)):
                point_feature.SetField(field_names[i], line_info[i])

            # 全部设置完了之后，添加到layer中
            layer.CreateFeature(point_feature)
            # 关闭feature
            point_feature = None
    except Exception as e:
        print(e)
    # 关闭文件的datasource
    data_source = None
    print("转换完成：" + csv_path)


# 递归文件夹，找到指定的文件后缀，返回数组
ext_paths = []
def recursion_folder(folder_path, extension):
    path_dir = os.listdir(folder_path)
    for sub in path_dir:
        sub_dir = os.path.join(folder_path, sub)
        if os.path.isfile(sub_dir):
            if os.path.splitext(sub_dir)[1] == extension:
                ext_paths.append(sub_dir)
        else:
            recursion_folder(sub_dir, extension)
    return ext_paths


if __name__ == '__main__':
    # 遍历文件夹内所有的csv文件
    batch_csv_path = "C:\\Users\\Administrator\\Desktop\\cxy"
    csv_paths = recursion_folder(batch_csv_path, ".csv")
    for csv_path in csv_paths:
        shp_path = os.path.splitext(csv_path)[0] + ".shp"
        csv2shp(csv_path, shp_path)
