import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import seaborn as sns
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Load data
merged = pd.read_csv('../outputs/utah_sewer_connectivity.csv')

shapefile_cousub = gpd.read_file('../data/geography_files/tl_2021_49_cousub/tl_2021_49_cousub.shp')
shapefile_cousub = shapefile_cousub[['COUSUBFP', 'geometry']]
shapefile_cousub['COUSUBFP'] = shapefile_cousub['COUSUBFP'].astype('int')
shapefile_cousub.rename({'COUSUBFP':'county_subdivision_fips'}, axis = 'columns', inplace = True)

merged = shapefile_cousub.merge(merged, on ='county_subdivision_fips', how = 'right')

# Make plot

fig, ax = plt.subplots(1,1)
merged.plot('percent_collection', ax=ax, legend = True)
shapefile_cousub.boundary.plot(ax=ax, color = 'gray', linewidth = 0.4)
plt.title('% of population receiving collection \nby county subdivision in Utah')
ax.set_axis_off()
plt.savefig('../figures/figsi_utah_sewer_connectivity_map.png')
plt.savefig('../figures/figsi_utah_sewer_connectivity_map.pdf')