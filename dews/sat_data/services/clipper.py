import os
import fiona
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
import matplotlib.pyplot as plt

band_path = "/home/jtrvz/Documents/sid/sentinel-2a/msi-l2a/S2A_MSIL2A_20230708T102601_N0509_R108_T32UNE_20230708T181859.SAFE/GRANULE/L2A_T32UNE_A042004_20230708T103512/IMG_DATA/R60m/"
band_names = os.listdir(band_path)
print(band_names)

shape_file = "/home/jtrvz/Documents/sid/sentinel-2a/msi-l2a/S2A_MSIL2A_20230708T102601_N0509_R108_T32UNE_20230708T181859.SAFE.shp"
aoi_file = fiona.open(shape_file)
aoi_gem = [aoi_file[0]["geometry"]]

