import pandas as pd
import numpy as np
import math
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Load data
wins = pd.read_csv('../data/minnesota/WINS data_annotated.csv')
wins = wins.dropna(subset = ['Census Place'], axis = 'index')
wins.reset_index(inplace = True, drop = True)

shapefile = gpd.read_file('../data/geography_files/tl_2021_27_place/tl_2021_27_place.shp')
shapefile_cousub = gpd.read_file('../data/geography_files/tl_2021_27_cousub/tl_2021_27_cousub.shp')
shapefile = shapefile.to_crs(epsg=3395) # Mercator projection
shapefile_cousub = shapefile_cousub.to_crs(epsg=3395) # Mercator projection

# Merge Minnesota WINS data with shapefile

merged = shapefile.merge(wins, left_on = 'NAME', right_on = 'Census Place', how = 'outer', indicator = True)
merged['Does your community have a collection system? '] = merged['Does your community have a collection system? '].fillna('Not reported')

# Print summary statistic

for value, df in merged.groupby('Does your community have a collection system? '):
    print(value, len(df))
    
# Make plot
fig, ax = plt.subplots()
ax.axis('off')
palette = {'Yes':'green', 'Not reported':'lightgrey', 'No':'red'}
legend_elements = []
for ctype, data in merged.groupby('Does your community have a collection system? '):
    data.plot(ax = ax, color = palette[ctype], label = ctype)
    legend_elements.append(Patch(facecolor=palette[ctype], label = ctype))
ax.legend(handles = legend_elements, loc = (0.7, 0.2))
shapefile_cousub.boundary.plot(ax = ax, linewidth = 0.2, color = 'gray')
plt.title('Existence of sewer collection systems \nby Census Designated Place in Minnesota (2021)')
plt.tight_layout()
plt.savefig('../figures/figsi_minnesota_sewer_connectivity_by_community.png')
plt.savefig('../figures/figsi_minnesota_sewer_connectivity_by_community.pdf')