import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
from scipy.stats import pearsonr
import matplotlib
import matplotlib.patches as mpatches
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

county_collections = pd.read_csv('../outputs/epa_sewer_connectivity_by_county_census.csv', index_col = 0)

state_fips_to_abbrev = pd.read_csv('../data/geography_files/state_fips_to_abbrev.txt', delimiter = '|')
state_fips_to_abbrev = state_fips_to_abbrev[['STATE', 'STUSAB']]
state_fips_to_abbrev.rename({'STATE':'STATEFP', 'STUSAB':'STATE'}, axis = 'columns', inplace = True)

shapefile = gpd.read_file('../data/geography_files/tl_2012_us_county/tl_2012_us_county.shp')
shapefile = shapefile.to_crs(epsg=3395)
shapefile['STATEFP']=shapefile['STATEFP'].astype('int')
shapefile = shapefile.merge(state_fips_to_abbrev, on = 'STATEFP')
shapefile = shapefile[['STATE', 'STATEFP', 'NAME', 'NAMELSAD', 'COUNTYFP', 'geometry']]
shapefile['STATEFP'] = shapefile['STATEFP'].astype('int')
shapefile['COUNTYFP'] = shapefile['COUNTYFP'].astype('int')
shapefile.rename({'NAME':'COUNTY'}, axis ='columns', inplace =True)

# Manually fixing discrepancies between county names in census shapefile and EPA data

# Finding duplicate rows in the shapefile county name and specifying whether the county name refers to a city

shapefile_duplicate_rows = shapefile[shapefile.duplicated(subset = ['STATE', 'COUNTY'], keep=False)]

# print(shapefile_duplicate_rows)
for i in shapefile_duplicate_rows.index:
    if shapefile_duplicate_rows.loc[i,'NAMELSAD'].find('city')>=0:
        shapefile.at[i,'COUNTY'] = shapefile_duplicate_rows.loc[i,'NAMELSAD'].title()
        
merged = shapefile.merge(county_collections, on = ['STATE', 'STATEFP', 'COUNTY', 'NAMELSAD', 'COUNTYFP'], how = 'right')

# Get discrete thresholds

merged['less_5%'] = False
merged.loc[merged['frac_pres_res_collection']<0.05, 'less_5%'] = True
merged['less_10%'] = False
merged.loc[merged['frac_pres_res_collection']<0.10, 'less_10%'] = True
merged['less_20%'] = False
merged.loc[merged['frac_pres_res_collection']<0.20, 'less_20%'] = True
merged['collection_category'] = '>=20%'

# Pulling out states with the most reliable data: New York, California, Florida, New Jersey, Maryland, Iowa, Minnesota, and Michigan

states = {'California':6,
          'Florida':12,
            'Iowa':19, 
         'Maryland':24,
         'Michigan':26,
         'Minnesota':27,
         'New Jersey':34,
          'New York':36}

# Plot continuous sewer connectivity

fig, ax_overall = plt.subplots(2, 4, figsize = (8,4))
i=0
j=0
for state in states:
    ax = ax_overall[i,j]
    merged_fl = merged[merged['STATEFP']==states[state]]
    merged_fl[merged_fl['below_1_flag']].plot(ax = ax, column = 'frac_pres_res_collection', categorical = False, legend = False, vmin = 0, vmax = 1, legend_kwds={'label': "Fraction of present resident population receiving collection",'orientation': "horizontal"})
    if len(merged_fl[~merged_fl['below_1_flag']])>0:
        merged_fl[~merged_fl['below_1_flag']].plot(ax = ax, column = 'below_1_flag', categorical = True, color = '#FDE725FF')
    if len(merged_fl[~merged_fl['epa_data']])>0:
        merged_fl[~merged_fl['epa_data']].plot(ax = ax, column = 'epa_data', categorical = True, color = 'lightgrey')
    merged_fl.boundary.plot(ax = ax, color = 'lightgrey', linewidth = 0.4)
    ax.set_axis_off()
    if j==3:
        i+=1
        j=0
    else:
        j+=1
    
    ax.set_title(state)
plt.suptitle("Fraction of resident population receiving collection")
plt.tight_layout()
plt.savefig('../figures/epa_sewer_connectivity_continuous.png', dpi = 300)
plt.savefig('../figures/epa_sewer_connectivity_continuous.pdf', dpi = 300)

# Plot discrete sewer connectivity

fig, ax_overall = plt.subplots(2, 4, figsize = (8,4))
i=0
j=0
for state in states:
    ax = ax_overall[i,j]
    merged_fl = merged[merged['STATEFP']==states[state]]
    merged_fl[merged_fl['less_20%']].plot(ax = ax_overall[i,j], column = 'less_20%', color = 'tab:orange')
    merged_fl[~merged_fl['less_20%']].plot(ax = ax_overall[i,j], column = 'less_20%', color = 'tab:blue')
    if len(merged_fl[~merged_fl['epa_data']])>0:
        merged_fl[~merged_fl['epa_data']].plot(ax = ax, column = 'epa_data', categorical = True, color = 'lightgrey')
    merged_fl.boundary.plot(ax = ax, color = 'lightgrey', linewidth = 0.4)
    ax.set_axis_off()
    if j==3:
        i+=1
        j=0
    else:
        j+=1
    
    ax.set_title(state)
orange_patch = mpatches.Patch(color='tab:orange', label='<20%')
blue_patch = mpatches.Patch(color='tab:blue', label='>=20%')

plt.suptitle("Fraction of resident population receiving collection")
plt.tight_layout()
plt.savefig('../figures/figsi_epa_sewer_connectivity_discrete.png', dpi = 300)
plt.savefig('../figures/figsi_epa_sewer_connectivity_discrete.pdf', dpi = 300)
