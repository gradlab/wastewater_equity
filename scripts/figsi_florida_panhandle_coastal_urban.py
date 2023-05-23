import pandas as pd
import numpy as np
import math
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, ttest_ind
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Plot map of percentage of Florida county subdivisions not connected to septic for particular geographical delineations (panhandle vs not panhandle, coastal vs inland, metro vs micro vs rural county subdivision)

# Uses output of florida_septic_analysis.py

septic_tanks = pd.read_csv('../outputs/florida_septic_inspections_by_county_subdivision_census.csv', index_col = 0)

# Load geospatial data
shapes = gpd.read_file('../data/geography_files/tl_2012_12_cousub/tl_2012_12_cousub.shp')
shapes = shapes[['COUSUBFP', 'geometry']]
shapes.rename({'COUSUBFP':'county_subdivision_fips'}, axis = 'columns', inplace = True)
shapes['county_subdivision_fips'] = shapes['county_subdivision_fips'].astype('int')

# Merge septic tank data with geospatial locations of counties

septic_tanks = shapes.merge(septic_tanks, on = 'county_subdivision_fips', how = 'right')

merged = septic_tanks.copy()

# Panhandle vs not panhandle

# The following counties (county fips) are always included in references to the panhandle (west of the Apalachicola River):
# - Bay County (5)
# - Calhoun County (13)
# - Escambia County (33)
# - Gulf County (45)
# - Holmes County (59)
# - Jackson County (63)
# - Okaloosa County (91)
# - Santa Rosa County (113)
# - Walton County (131)
# - Washington County (133)

panhandle_county_fips = [5, 13, 33, 45, 59, 63, 91, 113, 131, 133]
merged['in_panhandle']=False
for i in panhandle_county_fips:
    merged.loc[merged['county_fips']==i, 'in_panhandle'] = True
    
fig, ax = plt.subplots()
merged[~merged['in_panhandle']].plot(ax = ax, column = 'in_panhandle', color='tab:blue')
merged[merged['in_panhandle']].plot(ax = ax, column = 'in_panhandle', color='tab:orange')
shapes.boundary.plot(ax=ax, color = 'lightgrey', linewidth = 0.4)
ax.axis('off')
plt.savefig('../figures/figsi_florida_not_septic_panhandle_map.png')
plt.savefig('../figures/figsi_florida_not_septic_panhandle_map.pdf')

plt.figure(figsize = (3,4))
sns.boxplot(merged, x = 'in_panhandle', y = 'percentage_not_septic')
cmap = plt.get_cmap()
sns.stripplot(merged, x = 'in_panhandle', y = 'percentage_not_septic', color = 'gray', edgecolor = 'k', linewidth = 0.5, alpha = 0.5)
plt.xlabel('')
plt.ylabel('% of households not on septic')
plt.xticks(ticks = [0, 1], labels = ['Not in panhandle', 'In panhandle'], rotation = 90)
plt.savefig('../figures/figsi_florida_not_septic_panhandle.png')
plt.savefig('../figures/figsi_florida_not_septic_panhandle.pdf')

# Print summary stats

summary_geography = pd.DataFrame()
for value, df in merged.groupby('in_panhandle'):
    print('in_panhandle', value, np.median(df['percentage_not_septic']))
pvalue = ttest_ind(merged[merged['in_panhandle']]['percentage_not_septic'], merged[~merged['in_panhandle']]['percentage_not_septic'], equal_var=False)[1]
print('pvalue', pvalue)

# Coastal vs inland

# Assigning coastal county sudivisions by eye (county subdivision has coast) since there doesn't seem to be a list online at the county subdivision level (I did find a list for coastal counties, but they included inland county subdivisions in a coastal county)

coastal_cousub_fips = [92691,92309,91170,93542,92639,92145,92863,
                      90039,90429,93627,90949,93523,92704,92717,
                      90702,90468,90715,91475,92860,92327,93380,
                      90572,90182,93036,93042,93003,90273,91963,
                      93107,91393,93484,90975,91352,90195,93094,
                      90988,92301,92048,91027,90416,92210,91976,
                      91755,93471,91534,91729,92171,91417,91508,
                      91098,92782,90806,90208,90260,91872,93614,
                      92977,91690,92873,93250,91547,91157,93510,
                      92119,91573,90611,93224,92340,93159,92418,
                      91092,92080,93016,92795,91640,91644,91079]

merged['coastal']=False
for i in coastal_cousub_fips:
    merged.loc[merged['county_subdivision_fips']==i, 'coastal'] = True
    
fig, ax = plt.subplots()
merged[~merged['coastal']].plot(ax = ax, column = 'coastal', color='tab:blue')
merged[merged['coastal']].plot(ax = ax, column = 'coastal', color='tab:orange')
shapes.boundary.plot(ax=ax, color = 'lightgrey', linewidth = 0.4)
ax.axis('off')
plt.savefig('../figures/figsi_florida_not_septic_coastal_map.png')
plt.savefig('../figures/figsi_florida_not_septic_coastal_map.pdf')

plt.figure(figsize = (3,4))
sns.boxplot(merged, x = 'coastal', y = 'percentage_not_septic')
sns.stripplot(merged, x = 'coastal', y = 'percentage_not_septic', color = 'gray', edgecolor = 'k', linewidth = 0.5, alpha = 0.5)
plt.xlabel('')
plt.ylabel('% of households on septic')
plt.xticks(ticks = [0, 1], labels = ['Not coastal', 'Coastal'], rotation = 90)
plt.savefig('../figures/figsi_florida_not_septic_coastal.png')
plt.savefig('../figures/figsi_florida_not_septic_coastal.pdf')

# Print summary stats

summary_geography = pd.DataFrame()
for value, df in merged.groupby('coastal'):
    print('coastal', value, np.median(df['percentage_not_septic']))
pvalue = ttest_ind(merged[merged['coastal']]['percentage_not_septic'], merged[~merged['coastal']]['percentage_not_septic'], equal_var=False)[1]
print('pvalue', pvalue)

# Metro vs micro vs rural

fig, ax = plt.subplots()
merged[merged['metro_micro']=='Metropolitan Statistical Area'].plot(ax = ax, color='tab:blue')
merged[merged['metro_micro']=='Micropolitan Statistical Area'].plot(ax = ax, color='tab:orange')
merged[merged['metro_micro']=='Rural Area'].plot(ax = ax, color='tab:green')
shapes.boundary.plot(ax=ax, color = 'lightgrey', linewidth = 0.4)
ax.axis('off')
plt.savefig('../figures/figsi_florida_not_septic_urban_map.png')
plt.savefig('../figures/figsi_florida_not_septic_urban_map.pdf')

plt.figure(figsize = (3,4))
sns.boxplot(merged, x = 'metro_micro', y = 'percentage_not_septic')
sns.stripplot(merged, x = 'metro_micro', y = 'percentage_not_septic', color = 'gray', edgecolor = 'k', linewidth = 0.5, alpha = 0.5)
plt.xlabel('')
plt.ylabel('% of households not on septic')
plt.xticks(ticks = [0, 1, 2], labels = ['Metropolitan', 'Micropolitan', 'Rural'], rotation = 90)
plt.savefig('../figures/figsi_florida_not_septic_urban.png')
plt.savefig('../figures/figsi_florida_not_septic_urban.pdf')

# Print summary stats
summary_geography = pd.DataFrame()
for value, df in merged.groupby('metro_micro'):
    print('metro_micro', value, np.median(df['percentage_not_septic']))
pvalue = ttest_ind(merged[merged['metro_micro']=='Micropolitan Statistical Area']['percentage_not_septic'], merged[merged['metro_micro']=='Metropolitan Statistical Area']['percentage_not_septic'], equal_var=False)[1]
print('pvalue metro vs micro', pvalue)
pvalue = ttest_ind(merged[merged['metro_micro']=='Micropolitan Statistical Area']['percentage_not_septic'], merged[merged['metro_micro']=='Rural Area']['percentage_not_septic'], equal_var=False)[1]
print('pvalue micro vs rural', pvalue)