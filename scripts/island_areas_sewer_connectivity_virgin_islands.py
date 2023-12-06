import pandas as pd
import numpy as np
import math
import geopandas as gpd

# Load three sets of census data
# demographic data
census_dp1 = pd.read_csv('../data/islands/virgin_islands/DECENNIALDPVI2020.DP1-Data.csv')
census_dp1 = census_dp1[1:]
census_dp1.reset_index(inplace = True, drop = True)

# economic data (at household level)
census_dp3 = pd.read_csv('../data/islands/virgin_islands/DECENNIALDPVI2020.DP3-Data.csv')
census_dp3 = census_dp3[1:]
census_dp3.reset_index(inplace = True, drop = True)

# household size and composition data
census_dp4 = pd.read_csv('../data/islands/virgin_islands/DECENNIALDPVI2020.DP4-Data.csv')
census_dp4 = census_dp4[1:]
census_dp4.reset_index(inplace = True, drop = True)

census_island = census_dp1.merge(census_dp3, on = ['GEO_ID', 'NAME'])
census_island = census_island.merge(census_dp4, on = ['GEO_ID', 'NAME'])

# Extract county fips from geo id
geo_ids = census_island['GEO_ID'].values
county_subdivision_fips = []
for geo_id in geo_ids: 
    county_subdivision_fips.append(int(geo_id[geo_id.find('US78')+4:]))
census_island['place_fips'] = county_subdivision_fips

census_island['island'] = 'Virgin Is.'

census = census_island.copy()

census[census == '*****'] = np.nan
census[census == '***'] = np.nan
census[census == '**'] = np.nan
census[census == '-'] = np.nan
census[census == '100-'] = np.nan
census[census == '200-'] = np.nan
census[census == '2000+'] = np.nan
census[census == '2,500-'] = np.nan
census[census == '2500-'] = np.nan
census[census == '3000+'] = np.nan
census[census == '250,000+'] = np.nan
census[census == '1000000+'] = np.nan
census[census == 'null'] = np.nan
census[census == '(X)'] = np.nan
census[census == 'N'] = np.nan

# Convert all estimates and percentages into floats

column_headers = census.columns
float_headers = []
for column_header in column_headers:
    if column_header[:4]=='DP1_':
        if (column_header[8:]=='C') or (column_header[8:]=='P'):
            float_headers.append(column_header)
    if column_header[:4]=='DP3_':
        if (column_header[8:]=='C') or (column_header[8:]=='P'):
            float_headers.append(column_header)
    if column_header[:4]=='DP4_':
        if (column_header[8:]=='C') or (column_header[8:]=='P'):
            float_headers.append(column_header)
            
census[float_headers] = census[float_headers].astype('float')

# Get shapefile and merge with census data
shapes_filename = '../data/geography_files/tl_2020_78_place/tl_2020_78_place.shp'
shapes = gpd.read_file(shapes_filename)

shapes = shapes[['PLACEFP', 'NAMELSAD', 'geometry']]
shapes.rename({'PLACEFP':'place_fips', 'NAMELSAD':'place_name'}, axis = 'columns', inplace = True)

shapes['place_fips'] = shapes['place_fips'].astype('int')

merged = shapes.merge(census, on = ['place_fips'], how = 'outer')
merged.drop(['GEO_ID', 'NAME', 'Unnamed: 582'], inplace = True, axis = 'columns')

# Threshold on CDPs with at least 20 population and 5 households
total_pop_var = 'DP1_0001C'
total_households_var = 'DP1_0137C'
pop_thresh = 20
households_thresh = 5

pop_size = merged[total_pop_var].sum()
num_households = merged[total_households_var].sum()

merged = merged[merged[total_pop_var]>=pop_thresh]
merged = merged[merged[total_households_var]>=households_thresh]
merged.reset_index(inplace = True, drop = True)

print('% population size after threshold = ', merged[total_pop_var].sum()/pop_size)
print('% households after threshold = ', merged[total_households_var].sum()/num_households)

# Calculate fraction sewered
merged['frac_sewer'] = census['DP4_0062C']/census['DP4_0061C']
merged['frac_septic'] = census['DP4_0063C']/census['DP4_0061C']
merged['frac_other'] = census['DP4_0064C']/census['DP4_0061C']

# Summary stats
print('Overall fraction of households on sewer: ' + str(census['DP4_0062C'].sum()/census['DP4_0061C'].sum()))
print('Median fraction of households on sewer: ' + str(np.nanmedian(merged['frac_sewer'])))

# Save data
merged.drop('geometry', axis = 'columns', inplace = True)
merged.to_csv('../outputs/island_areas_sewer_connectivity_virgin_islands.csv')