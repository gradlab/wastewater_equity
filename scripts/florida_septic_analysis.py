import pandas as pd
import numpy as np
import math

# Import and clean data
septic_tanks = pd.read_csv('../outputs/florida_septic_inspections_by_county_subdivision.csv', index_col = 0)

# Load census data

# demographic data
census_dp = pd.read_csv('../data/acs/florida_county_subdivision_2012/ACSDP5Y2012.DP05-Data.csv')
census_dp = census_dp[1:]
census_dp.reset_index(inplace = True, drop = True)

# economic data (at household level)
census_st = pd.read_csv('../data/acs/florida_county_subdivision_2012/ACSST5Y2012.S1903-Data.csv')
census_st = census_st[1:]
census_st.reset_index(inplace = True, drop = True)

# household size and composition data
census_sts1101 = pd.read_csv('../data/acs/florida_county_subdivision_2012/ACSST5Y2012.S1101-Data.csv')
census_sts1101 = census_sts1101[1:]
census_sts1101.reset_index(inplace = True, drop = True)

# insurance coverage
census_sts2701 = pd.read_csv('../data/acs/florida_county_subdivision_2012/ACSST5Y2012.S2701-Data.csv')
census_sts2701 = census_sts2701[1:]
census_sts2701.reset_index(inplace = True, drop = True)

census = census_dp.merge(census_st, on = ['GEO_ID', 'NAME'])
census = census.merge(census_sts1101, on = ['GEO_ID', 'NAME'])
census = census.merge(census_sts2701, on = ['GEO_ID', 'NAME'])
census[census == '*****'] = np.nan
census[census == '***'] = np.nan
census[census == '**'] = np.nan
census[census == '-'] = np.nan
census[census == '2,500-'] = np.nan
census[census == '250,000+'] = np.nan
census[census == 'null'] = np.nan
census[census == '(X)'] = np.nan

# Extract county fips from geo id
geo_ids = census['GEO_ID'].values
county_subdivision_fips = []
for geo_id in geo_ids: 
    county_subdivision_fips.append(int(geo_id[geo_id.find('US12')+7:]))
census['county_subdivision_fips'] = county_subdivision_fips

# Convert all estimates and estimate errors in census data to floats
column_headers = census.columns
float_headers = []
for column_header in column_headers:
    if column_header[:5]=='DP05_':
        if (column_header[9:]=='E') or (column_header[9:]=='M') or (column_header[9:]=='PE') or (column_header[9:]=='PM'):
            float_headers.append(column_header)
    if column_header[:6]=='S1903_':
        if (column_header[13:]=='E') or (column_header[13:]=='M'):
            float_headers.append(column_header)
    if column_header[:6]=='S1101_':
        if (column_header[13:]=='E') or (column_header[13:]=='M'):
            float_headers.append(column_header)
    if column_header[:6]=='S2701_':
        if (column_header[13:]=='E') or (column_header[13:]=='M'):
            float_headers.append(column_header)
            
census[float_headers] = census[float_headers].astype('float')

# Merge septic tank and census datasets

merged = septic_tanks.merge(census, on = 'county_subdivision_fips', how = 'outer')
merged.drop(['GEO_ID', 'NAME'], inplace = True, axis = 'columns')

# Thresholding on at least 5 households and at least a population of 20
total_pop_var = 'DP05_0028E'
total_households_var = 'DP05_0081E'
pop_thresh = 20
households_thresh = 5

pop_size = merged[total_pop_var].sum()
num_households = merged[total_households_var].sum()

merged = merged[merged[total_pop_var]>=pop_thresh]
merged = merged[merged[total_households_var]>=households_thresh]

print('% population size after threshold = ', merged[total_pop_var].sum()/pop_size)
print('% households after threshold = ', merged[total_households_var].sum()/num_households)

# Use the census data to calculate the fraction of households on septic

merged['frac_septic'] = merged['num_septic_tanks']/merged['DP05_0081E']   #DP05_0086E: total housing units
merged['frac_not_septic'] = 1-merged['frac_septic']

merged.replace({'frac_septic':{np.inf:np.nan}}, inplace = True)
merged.replace({'frac_not_septic':{np.inf:np.nan}}, inplace = True)

merged['percentage_not_septic'] = 100*merged['frac_not_septic']
merged['percentage_septic'] = 100*merged['frac_septic']

merged.to_csv('../outputs/florida_septic_inspections_by_county_subdivision_census.csv')