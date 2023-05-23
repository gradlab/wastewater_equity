import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Load percent sewered output from ahs_census_division.py

percent_sewered_df = pd.read_csv('../outputs/ahs_sewer_connectivity_by_census_division.csv', index_col = 0)

# Load shapefile and merge with percent sewered data

shapefile = gpd.read_file('../data/geography_files/cb_2021_us_division_500k/cb_2021_us_division_500k.shp')

shapefile = shapefile.to_crs(epsg=3395) # Mercator projection

percent_sewered_df_overall_sorted = percent_sewered_df[percent_sewered_df['variable_type']=='overall'].sort_values('percent_sewered', ascending = False)

merged = shapefile.merge(percent_sewered_df_overall_sorted, left_on = 'NAME', right_on = 'geo_description')

# Plot

fig, ax = plt.subplots()
ax.axis('off')
merged.plot('percent_sewered', ax = ax, legend = True, vmin = 60, vmax = 100, legend_kwds = {'orientation':'horizontal', 'shrink':0.3, 'label':'% of households connected to sewer'})
shapefile.boundary.plot(ax = ax, color = 'grey', linewidth = 0.2)
ax.set_xlim([-1.5*10**7, -0.7*10**7])
ax.set_ylim([0.2*10**7, 0.7*10**7])

akax = fig.add_axes([0.05, 0.2, 0.3, 0.35])   
akax.axis('off')
merged.plot('percent_sewered', ax = akax, vmin = 60, vmax = 100)
shapefile.boundary.plot(ax = akax, color = 'grey', linewidth = 0.2)
akax.set_xlim([-2*10**7, -1.5*10**7])
akax.set_ylim([0.6*10**7, 1.3*10**7])

hiax = fig.add_axes([0.28, 0.3, 0.2, 0.19])   
hiax.axis('off')
merged.plot('percent_sewered', ax = hiax, vmin = 60, vmax = 100)
shapefile.boundary.plot(ax = hiax, color = 'grey', linewidth = 0.2)
hiax.set_xlim([-1.8*10**7, -1.7*10**7])
hiax.set_ylim([0.2*10**7, 0.26*10**7])

plt.tight_layout()
plt.savefig('../figures/fig1_sewer_connectivity_by_census_division.png', dpi = 300)
plt.savefig('../figures/fig1_sewer_connectivity_by_census_division.pdf', dpi = 300)