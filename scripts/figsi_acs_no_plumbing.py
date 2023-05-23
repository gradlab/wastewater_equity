import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import geopandas as gpd
import os
from zipfile import ZipFile
from urllib import request

# Load ACS table DP04

# social characteristics
census = pd.read_csv('../data/acs/us_county_2021/ACSDP5Y2021.DP04-Data.csv')
census = census[1:]
census.reset_index(inplace = True, drop = True)

census[census == '*****'] = np.nan
census[census == '***'] = np.nan
census[census == '**'] = np.nan
census[census == '-'] = np.nan
census[census == '2,500-'] = np.nan
census[census == '250,000+'] = np.nan
census[census == 'null'] = np.nan
census[census == '(X)'] = np.nan
census[census == 'N'] = np.nan
census[census == '9.0+'] = np.nan
census[census == '4,000+'] = np.nan
census[census == '100-'] = np.nan

# Extract county fips from geo id
geo_ids = census['GEO_ID'].values
state_fips = []
county_fips = []
for geo_id in geo_ids: 
    state_fips.append(int(geo_id[geo_id.find('US')+2:geo_id.find('US')+4]))
    county_fips.append(int(geo_id[geo_id.find('US')+4:]))
census['state_fips'] = state_fips
census['county_fips'] = county_fips

# Convert appropriate column values to floats
column_headers = census.columns
float_headers = []
for column_header in column_headers:
    if column_header[:5]=='DP04_':
        if (column_header[9:]=='E') or (column_header[9:]=='M') or (column_header[9:]=='PE') or (column_header[9:]=='PM'):
            float_headers.append(column_header)
            
census[float_headers] = census[float_headers].astype('float')

# Download shapefile and merge with data

if not os.path.exists('../data/geography_files/tl_2021_us_county/'):
    request.urlretrieve('https://www2.census.gov/geo/tiger/TIGER2021/COUNTY/tl_2021_us_county.zip', '../data/geography_files/tl_2021_us_county.zip')

    # Unzip metadata file
    if not os.path.exists('../data/geography_files/tl_2021_us_county/'):
        os.mkdir('../data/geography_files/tl_2021_us_county/')
        with ZipFile('../data/geography_files/tl_2021_us_county.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/geography_files/tl_2021_us_county/')
    # Delete zip file
    os.remove('../data/geography_files/tl_2021_us_county.zip')

shapefile = gpd.read_file('../data/geography_files/tl_2021_us_county/tl_2021_us_county.shp')

shapefile = shapefile[['STATEFP', 'COUNTYFP', 'NAME', 'geometry']]
shapefile.rename({'STATEFP':'state_fips', 'COUNTYFP':'county_fips', 'NAME':'county'}, axis = 'columns', inplace = True)

shapefile['state_fips'] = shapefile['state_fips'].astype('int')
shapefile['county_fips'] = shapefile['county_fips'].astype('int')
shapefile = shapefile.to_crs(epsg=3395) # Mercator projection

merged = shapefile.merge(census, on = ['state_fips', 'county_fips'], how = 'right', indicator = True)

# Make plot
fig, ax = plt.subplots(figsize = (5,5))
merged.plot('DP04_0073PE', ax = ax, legend = True, legend_kwds={"orientation": "horizontal"})
plt.title('Percent of occupied housing units lacking \ncomplete plumbing facilities by county')
plt.xlim([-2.1*10**7, -0.7*10**7])
ax.set_axis_off()
plt.savefig('../figures/figsi_acs_no_plumbing.png')
plt.savefig('../figures/figsi_acs_no_plumbing.pdf')

# Save table
merged_subset = merged[['NAME', 'DP04_0073PE']]
merged_subset.rename({'NAME':'County, State', 'DP04_0073PE':'Percent of occupied housing units lacking complete plumbing facilities'}, axis = 'columns', inplace = True)

merged_subset.sort_values('Percent of occupied housing units lacking complete plumbing facilities', ascending = False, inplace = True)
merged_subset.reset_index(inplace = True, drop = True)
merged_subset.to_csv('../outputs/tablesi_acs_no_plumbing.csv')

