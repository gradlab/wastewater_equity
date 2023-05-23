import pandas as pd
import numpy as np
import math
import geopandas as gpd
from shapely.geometry import Point
import os
from zipfile import ZipFile
from urllib import request

# Download and unzip data (too large to upload to github)

if not os.path.exists("../data/florida_septic_inspections/septic_jun12.zip"):
    request.urlretrieve("https://fgdl.org/zips/geospatial_data/archive/septic_jun12.zip", "../data/florida_septic_inspections/septic_jun12.zip")

# Unzip metadata file
if not os.path.exists("../data/florida_septic_inspections/septic_jun12/"):
    os.mkdir("../data/florida_septic_inspections/septic_jun12/")
    with ZipFile("../data/florida_septic_inspections/septic_jun12.zip", 'r') as zip_ref:
        zip_ref.extractall("../data/florida_septic_inspections/septic_jun12/")
        
septic = gpd.read_file("../data/florida_septic_inspections/septic_jun12/septic_jun12.shp")

# Remove entires that are not active
septic_active = septic[septic['STATESTATU']=='ACTIVE']

# Removing duplicates
# Will only keep the first entry with the same lattitude and longitude, and application date. 

septic_deduplicated = septic_active[~septic_active.duplicated(subset = ['LATITUDE', 'LONGITUDE', 'CURRENTAPP'])]
septic_deduplicated.reset_index(inplace = True, drop = True)

# Get the locations that have been repeatedly inspected (same longitude and latitude).
# For each group, get the indices of all but the most recent entry. Remove all but the most recent entry. 

septic_latest_inspec = septic_deduplicated.sort_values(by=['LATITUDE', 'LONGITUDE', 'CURRENTAPP'])
septic_latest_inspec.drop_duplicates(subset=['LATITUDE', 'LONGITUDE'], keep='last', inplace = True)
septic_latest_inspec.reset_index(inplace = True, drop = True)

# Print some summary statistics
print('total entries: ' + str(len(septic)))
print('active entries: ' + str(len(septic_active)))
print('after removing entries with the same latitude, longitude, and application date: ' + str(len(septic_deduplicated)))
print('after removing older entries with the same latitude and longitude: ' + str(len(septic_latest_inspec)))

# Compile septic tank locations into county subdivisions using latitude and longitude

septic = septic_latest_inspec.copy()
geometry = [Point(xy) for xy in zip(septic.LONGITUDE, septic.LATITUDE)]
septic_lat_long = gpd.GeoDataFrame(septic, geometry=geometry)

# Load county subdivisions shape file
county_sub = gpd.read_file('../data/geography_files/tl_2012_12_cousub/tl_2012_12_cousub.shp')

# Geographical join with septic tank locations
septic_county_sub = gpd.sjoin(septic_lat_long, county_sub)

septic_tanks_dict = {'county_subdivision_name':[], 'num_septic_tanks':[]}
for value, df in septic_county_sub.groupby('NAME'):
    septic_tanks_dict['county_subdivision_name'].append(value)
    septic_tanks_dict['num_septic_tanks'].append(len(df))
    
septic_tanks = pd.DataFrame(septic_tanks_dict)

# Merge back with shapefile to get fips codes and county subdivision geometries
county_sub.rename({'NAME':'county_subdivision_name'}, axis = 'columns', inplace = True)
septic_tanks_merged = county_sub.merge(septic_tanks, on = 'county_subdivision_name', how = 'left')

# When the # of septic tanks is nan, fill with 0
septic_tanks_merged['num_septic_tanks'] = septic_tanks_merged['num_septic_tanks'].fillna(0)

septic_tanks_merged = septic_tanks_merged[['county_subdivision_name', 'COUSUBFP', 'COUNTYFP', 'num_septic_tanks', 'geometry']]
septic_tanks_merged.rename({'COUSUBFP':'county_subdivision_fips','COUNTYFP':'county_fips'}, axis = 'columns', inplace = True)
septic_tanks_merged['county_subdivision_fips'] = septic_tanks_merged[['county_subdivision_fips']].astype('int')
septic_tanks_merged['county_fips'] = septic_tanks_merged[['county_fips']].astype('int')
septic_tanks_merged['num_septic_tanks'] = septic_tanks_merged[['num_septic_tanks']].astype('int')
septic_tanks_merged.sort_values(by = 'county_subdivision_name', ignore_index = True, inplace = True)
septic_tanks_merged['num_septic_tanks'].fillna(0, inplace = True)

# Load CBSA data
county2cbsa = pd.read_csv('../data/geography_files/cbsa2fipsxw.csv')
county2cbsa = county2cbsa[1:]
county2cbsa.reset_index(inplace = True, drop = True)
county2cbsa = county2cbsa[county2cbsa['statename']=='Florida']
county2cbsa.reset_index(inplace = True, drop = True)
county2cbsa = county2cbsa[['cbsacode', 'cbsatitle', 'metropolitanmicropolitanstatis', 'fipscountycode', 'centraloutlyingcounty']]
county2cbsa.rename({'cbsacode':'cbsa_fips', 'cbsatitle':'cbsa_name', 'metropolitanmicropolitanstatis':'metro_micro','fipscountycode':'county_fips', 'centraloutlyingcounty':'central_outlying_county'}, inplace = True, axis = 'columns')

# Merge septic and cbsa dataframes
septic_tanks_merged = septic_tanks_merged.merge(county2cbsa, on = 'county_fips', how = 'left')
septic_tanks_merged['metro_micro'].fillna('Rural Area', inplace = True)

if not os.path.exists('../outputs/'):
    os.mkdir('../outputs')

septic_tanks_df = septic_tanks_merged.drop('geometry', axis ='columns')
septic_tanks_df.to_csv('../outputs/florida_septic_inspections_by_county_subdivision.csv')
