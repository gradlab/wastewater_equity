import pandas as pd
import numpy as np
import math
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Plot map of percentage of Florida county subdivisions not connected to septic

# Uses output of florida_septic_analysis.py

# Load data
septic_tanks = pd.read_csv('../outputs/florida_septic_inspections_by_county_subdivision_census.csv', index_col = 0)

# Load geospatial data
shapes = gpd.read_file('../data/geography_files/tl_2012_12_cousub/tl_2012_12_cousub.shp')
shapes = shapes[['COUSUBFP', 'geometry']]
shapes.rename({'COUSUBFP':'county_subdivision_fips'}, axis = 'columns', inplace = True)
shapes['county_subdivision_fips'] = shapes['county_subdivision_fips'].astype('int')

# Merge septic tank data with geospatial locations of counties

septic_tanks = shapes.merge(septic_tanks, on = 'county_subdivision_fips', how = 'right')

# Print summary statistic
print('Overall percentage of households not on septic = ' + str(100*septic_tanks['num_septic_tanks'].sum()/septic_tanks['DP05_0081E'].sum()))

# Plot % county subdivision not on septic

fig, ax = plt.subplots(1,1)
ax.axis('off')
septic_tanks.plot(ax=ax, column = 'percentage_not_septic', categorical = False, legend = True, vmin = 50, vmax = 100)
shapes.boundary.plot(ax=ax, color = 'gray', linewidth = 0.4)

plt.xticks([])
plt.yticks([])
plt.title('% of households not on septic \nby county subdivision in Florida')
plt.tight_layout()
plt.savefig('../figures/fig4_florida_not_septic_by_county_subdivision.pdf')
plt.savefig('../figures/fig4_florida_not_septic_by_county_subdivision.png')

