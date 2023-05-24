import pandas as pd
import math
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# Load data
mwpp = pd.read_csv('../data/utah/Population-location-facility-type-county.csv')
mwpp.rename({'Location Latitude':'latitude', 'Location Longitude':'longitude'}, axis = 'columns', inplace = True)

# Note that small lagoons do collection and treatment.
# Filter to any facility that has any collection (i.e. collection only, or treatment and collection)

mwpp = mwpp[(mwpp['Type']=='COLLECTION')|(mwpp['Type']=='SMALL LAGOON')]
mwpp.reset_index(inplace = True, drop = True)

# Analysis by county subdivision

shapefile_cousub = gpd.read_file('../data/geography_files/tl_2021_49_cousub/tl_2021_49_cousub.shp')
shapefile_cousub['COUNTYFP'] = shapefile_cousub['COUNTYFP'].astype('int')
shapefile_cousub['COUSUBFP'] = shapefile_cousub['COUSUBFP'].astype('int')

# 5 facilities' lat and long did not fall within Utah:
# - BRIAN HEAD TOWN
# - CANYONG LAND IMPROVEMENT DISTRICT
# - HILL AFB (AMERICAN WATER)
# - JORDANELLE SSD
# - PLAIN CITY

# 1 facility did not report a lat and long
# - PANGUITCH LAKE S. S. D.

# For these, I manually edited the latitude and longitude to be what is found in google maps (or if it was a city, then I chose a particular location in that city to get the latitude and longitude for)

mwpp.loc[mwpp['Facility']=='BRIAN HEAD TOWN','latitude'] = 37.69427787758301
mwpp.loc[mwpp['Facility']=='BRIAN HEAD TOWN','longitude'] = -112.84776602429712

mwpp.loc[mwpp['Facility']=='CANYON LAND IMPROVEMENT DISTRICT','latitude'] = 38.24172056047709
mwpp.loc[mwpp['Facility']=='CANYON LAND IMPROVEMENT DISTRICT','longitude'] = -109.90888290402515

mwpp.loc[mwpp['Facility']=='HILL AFB (AMERICAN WATER)','latitude'] = 41.53048329470008
mwpp.loc[mwpp['Facility']=='HILL AFB (AMERICAN WATER)','longitude'] = -112.01565719606225

mwpp.loc[mwpp['Facility']=='JORDANELLE SSD','latitude'] = 40.572839011318905
mwpp.loc[mwpp['Facility']=='JORDANELLE SSD','longitude'] = -111.42657524724493

mwpp.loc[mwpp['Facility']=='PLAIN CITY','latitude'] = 41.30154861748692
mwpp.loc[mwpp['Facility']=='PLAIN CITY','longitude'] = -112.08110618960067

mwpp.loc[mwpp['Facility']=='PANGUITCH LAKE S. S. D.','latitude'] = 37.71613030466957
mwpp.loc[mwpp['Facility']=='PANGUITCH LAKE S. S. D.','longitude'] = -112.6399278730633

# Spatial join of locations of sewer systems with the county subdivision boundaries

geometry = [Point(xy) for xy in zip(mwpp.longitude, mwpp.latitude)]
mwpp_lat_long = gpd.GeoDataFrame(mwpp, geometry=geometry)

mwpp_cousub = gpd.sjoin(mwpp_lat_long, shapefile_cousub, how = 'left')

cousubs = []
pop_served = []
for cousub, df in mwpp_cousub.groupby('NAME'):
    cousubs.append(cousub)
    pop_served.append(df['Approximate population served'].sum())
mwpp_cousubs = pd.DataFrame({'county_subdivision':cousubs, 'collection_population':pop_served})

merged = shapefile_cousub.merge(mwpp_cousubs, left_on = 'NAME', right_on ='county_subdivision', how = 'outer')
merged['collection_population'] = merged['collection_population'].fillna(0)

merged = merged[['COUNTYFP', 'COUSUBFP', 'NAME', 'geometry', 'collection_population']]
merged.rename({'COUNTYFP':'county_fips', 'COUSUBFP':'county_subdivision_fips', 'NAME':'county_subdivision'}, axis = 'columns', inplace = True)

# Load census data

# social characteristics
census_dp2 = pd.read_csv('../data/acs/utah_county_subdivision_2021/ACSDP5Y2021.DP02-Data.csv')
census_dp2 = census_dp2[1:]
census_dp2.reset_index(inplace = True, drop = True)

# economics data (at household level)
census_dp3 = pd.read_csv('../data/acs/utah_county_subdivision_2021/ACSDP5Y2021.DP03-Data.csv')
census_dp3 = census_dp3[1:]
census_dp3.reset_index(inplace = True, drop = True)

# demographic data
census_dp5 = pd.read_csv('../data/acs/utah_county_subdivision_2021/ACSDP5Y2021.DP05-Data.csv')
census_dp5 = census_dp5[1:]
census_dp5.reset_index(inplace = True, drop = True)

census = census_dp2.merge(census_dp3, on = ['GEO_ID', 'NAME'])
census = census.merge(census_dp5, on = ['GEO_ID', 'NAME'])
census[census == '*****'] = np.nan
census[census == '***'] = np.nan
census[census == '**'] = np.nan
census[census == '-'] = np.nan
census[census == '2,500-'] = np.nan
census[census == '250,000+'] = np.nan
census[census == 'null'] = np.nan
census[census == '(X)'] = np.nan
census[census == 'N'] = np.nan

# Extract county fips from geo id
geo_ids = census['GEO_ID'].values
county_subdivision_fips = []
for geo_id in geo_ids: 
    county_subdivision_fips.append(int(geo_id[geo_id.find('US49')+7:]))
census['county_subdivision_fips'] = county_subdivision_fips

# Convert all estimates and estimate errors in census data to floats
column_headers = census.columns
float_headers = []
for column_header in column_headers:
    if column_header[:5]=='DP02_':
        if (column_header[9:]=='E') or (column_header[9:]=='M') or (column_header[9:]=='PE') or (column_header[9:]=='PM'):
            float_headers.append(column_header)
    if column_header[:5]=='DP03_':
        if (column_header[9:]=='E') or (column_header[9:]=='M') or (column_header[9:]=='PE') or (column_header[9:]=='PM'):
            float_headers.append(column_header)
    if column_header[:5]=='DP05_':
        if (column_header[9:]=='E') or (column_header[9:]=='M') or (column_header[9:]=='PE') or (column_header[9:]=='PM'):
            float_headers.append(column_header)
            
census[float_headers] = census[float_headers].astype('float')

# Merge septic tank and census datasets
merged = merged.merge(census, on = 'county_subdivision_fips', how = 'outer')
merged.drop(['GEO_ID', 'NAME'], inplace = True, axis = 'columns')

# Calculate fraction receiving collection
merged['frac_collection'] = merged['collection_population']/merged['DP05_0001E']   #DP05_0086E: total housing units
merged.replace({'frac_collection':{np.inf:np.nan}}, inplace = True)

# Filter to at least 5 households and at least a population size of 20
total_pop_var = 'DP05_0033E'
total_households_var = 'DP02_0001E'
pop_thresh = 20
households_thresh = 5

merged = merged[merged[total_pop_var]>=pop_thresh]
merged = merged[merged[total_households_var]>=households_thresh]

merged.reset_index(drop = True, inplace = True)

# Put max fraction of population receiving collection at 1
merged.loc[merged['frac_collection']>1,'frac_collection']=1

# Calculate percentage receiving and not receiving collection
merged['frac_not_collection']=1-merged['frac_collection']
merged['percent_collection']=100*merged['frac_collection']
merged['percent_not_collection']=100*merged['frac_not_collection']

# Save outputs
merged.drop('geometry', axis = 'columns', inplace = True)
merged.to_csv('../outputs/utah_sewer_connectivity.csv')