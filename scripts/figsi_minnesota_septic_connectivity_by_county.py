import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)
import os
from zipfile import ZipFile
from urllib import request

# Load data

ssts = pd.read_csv('../data/minnesota/ssts_data.csv')
ssts.rename({'Total SSTS\nreported\nin 2017':'num_ssts'}, axis = 'columns', inplace = True)

counties = ssts['County']
county_full_names = []
for county in counties:
    if county.find('*')>=0:
        county = county.replace('*', '')
    county_full_names.append(county + ' County, Minnesota')
ssts['county_full_name'] = county_full_names

# Load ACS data of number of households by county

acs = pd.read_csv('../data/acs/minnesota_county_2017/ACSDP5Y2017.DP05-Data.csv')
acs = acs[1:]
acs = acs[['GEO_ID', 'NAME', 'DP05_0086E']]
acs.rename({'NAME':'county_full_name', 'DP05_0086E':'households'}, axis = 'columns', inplace = True)

geo_ids = acs['GEO_ID']
county_fips = []
for geo_id in geo_ids:
    county_fips.append(int(geo_id[-3:]))
acs['county_fips'] = county_fips

# Download and unzip counties shapefile

if not os.path.exists('../data/geography_files/tl_2017_us_county/'):
    request.urlretrieve('https://www2.census.gov/geo/tiger/TIGER2017/COUNTY/tl_2017_us_county.zip', '../data/geography_files/tl_2017_us_county.zip')

    # Unzip metadata file
    if not os.path.exists('../data/geography_files/tl_2017_us_county/'):
        os.mkdir('../data/geography_files/tl_2017_us_county/')
        with ZipFile('../data/geography_files/tl_2017_us_county.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/geography_files/tl_2017_us_county/')
    # Delete zip file
    os.remove('../data/geography_files/tl_2017_us_county.zip')
    
# Load counties shapefile

shapefile = gpd.read_file('../data/geography_files/tl_2017_us_county/tl_2017_us_county.shp')
shapefile = shapefile[shapefile['STATEFP']=='27']
shapefile.rename({'COUNTYFP':'county_fips'}, axis = 'columns', inplace = True)
shapefile['county_fips'] = shapefile['county_fips'].astype('int')
shapefile = shapefile[['county_fips', 'geometry']]
shapefile = shapefile.to_crs(epsg=3395) # Mercator projection

# Merge the 3 datasets together
acs = shapefile.merge(acs, on = 'county_fips', how = 'outer')
merged = acs.merge(ssts, on = 'county_full_name', how = 'outer', indicator = True)

# Calculate percentage connected and not connected to septic systems
merged['percent_ssts'] = 100*merged['num_ssts'].astype('float')/merged['households'].astype('float')
merged['100-percent_ssts'] = 100-100*merged['num_ssts'].astype('float')/merged['households'].astype('float')

# Make plot
fig, ax = plt.subplots()
ax.axis('off')
merged.plot('100-percent_ssts', ax=ax, legend= True, vmin = 0, vmax = 100)
shapefile.boundary.plot(ax=ax, color = 'lightgrey', linewidth = 0.4)
plt.title('Percentage of households without \nsubsurface sewage treatment systems \nby county in Minnesota (2017)')
plt.tight_layout()
plt.savefig('../figures/figsi_minnesota_septic_connectivity_by_county.png')
plt.savefig('../figures/figsi_minnesota_septic_connectivity_by_county.pdf')