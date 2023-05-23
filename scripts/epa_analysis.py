import pandas as pd
import numpy as np
import math

# Load connectivity data
county_summary = pd.read_csv('../outputs/epa_sewer_connectivity_by_county.csv', index_col = 0)

# Load census data

# Load two sets of census data
# demographic data
census_dp = pd.read_csv('../data/acs/us_county_2012/ACSDP5Y2012.DP05-Data.csv')
census_dp = census_dp[1:]
census_dp.reset_index(inplace = True, drop = True)

# economic data (at household level)
census_st = pd.read_csv('../data/acs/us_county_2012/ACSST5Y2012.S1903-Data.csv')
census_st = census_st[1:]
census_st.reset_index(inplace = True, drop = True)

# household size and composition data
census_sts1101 = pd.read_csv('../data/acs/us_county_2012/ACSST5Y2012.S1101-Data.csv')
census_sts1101 = census_sts1101[1:]
census_sts1101.reset_index(inplace = True, drop = True)

# insurance coverage
census_sts2701 = pd.read_csv('../data/acs/us_county_2012/ACSST5Y2012.S2701-Data.csv')
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
state_fips = []
county_fips = []
for geo_id in geo_ids:
    state_fips.append(int(geo_id[geo_id.find('US')+2:geo_id.find('US')+4]))
    county_fips.append(int(geo_id[geo_id.find('US')+4:]))
census['STATEFP'] = state_fips
census['COUNTYFP'] = county_fips

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

# Merge wastewater and census df's together. Checked that all rows merged 1:1, except island areas were not in census data.

# Analyze island areas separately later.

merged = county_summary.merge(census, on = ['STATEFP', 'COUNTYFP'], how = 'inner')#, indicator = True)
merged.drop(['GEO_ID', 'NAME', 'Unnamed: 650_y'], inplace = True, axis = 'columns')

# Calculate fraction receiving collection

# I am using the total population size from the age/sex and race estimates (the same).

merged['frac_pres_res_collection'] = merged['PRES_RES_RECEIVING_COLLCTN']/merged['DP05_0001E']
merged['frac_pres_n_res_collection'] = merged['PRES_N_RES_RECEIVING_COLLCTN']/merged['DP05_0001E']

# Print summary stats

print('total fraction of present residents receiving collection = ' + str(np.sum(merged['PRES_RES_RECEIVING_COLLCTN'])/np.sum(merged['DP05_0001E'])))
print('mean fraction of present residents receiving collection = ' + str(np.mean(merged['frac_pres_res_collection'])))
print('median fraction of present residents receiving collection = ' + str(np.median(merged['frac_pres_res_collection'])))

# Flag counties with >1 of residents receiving collection

merged['below_1_flag']=True
merged.loc[merged['frac_pres_res_collection']>1,'below_1_flag']=False

# Save data
merged.to_csv('../outputs/epa_sewer_connectivity_by_county_census.csv')