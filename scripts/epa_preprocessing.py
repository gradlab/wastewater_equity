import pandas as pd
import numpy as np
import math
import geopandas as gpd
from unidecode import unidecode
import os
from zipfile import ZipFile
from urllib import request

# Download and unzip shapefile of all US counties (too large to upload to github)

if not os.path.exists('../data/geography_files/tl_2012_us_county/'):
    request.urlretrieve('https://www2.census.gov/geo/tiger/TIGER2012/COUNTY/tl_2012_us_county.zip', '../data/geography_files/tl_2012_us_county.zip')

    # Unzip metadata file
    if not os.path.exists('../data/geography_files/tl_2012_us_county/'):
        os.mkdir('../data/geography_files/tl_2012_us_county/')
        with ZipFile('../data/geography_files/tl_2012_us_county.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/geography_files/tl_2012_us_county/')
    # Delete zip file
    os.remove('../data/geography_files/tl_2012_us_county.zip')
    
# Filter by the facility type currently existing at a CWNS facility. 

# Focusing on facility types: 'Collection: Combined Sewers' and 'Collection: Separate Sewers'. Should also check what would happen if I included 'Colleciton: Interceptor Sewer', 'Collection: Pump Stations', and 'Treatment Lagoon or Pond'.

# I checked that the SUMMARY_FACILITY.csv and SUMMARY_FACILITY_TYPE.csv files give the same number of CWNS facilities when doing the above filtering. 

# Additionally, I'm using the "Receiving Collection" data for the population size: the total number who are connected to a sewer system which empties into a treatment plant. This does not include pouplations served by acceptable decentralized wastewater treatment systems, or populations connected to sewers that do not discharge to a treatment plant (i.e. upstream collection, clustered systems population, and onsite wastewater treatment systems population). 

facility_types =['Collection: Combined Sewers',
                'Collection: Separate Sewers']

facility_summary = pd.read_csv('../data/epa/SUMMARY_FACILITY.csv')
facility_summary = facility_summary[['CWNS_NUMBER', 
                                     'REGION', 
                                     'STATE', 
                                     'PRIMARY_COUNTY', 
                                     'SECONDARY_COUNTIES', 
                                     'LATITUDE', 
                                     'LONGITUDE', 
                                     'HORIZONTAL_COORDINATE_DATUM', 
                                     'SCALE',
                                     'PRES_FACILITY_TYPE',
                                     'PRES_FACILITY_OVERALL_TYPE']]

facility_summary['PRES_FACILITY_TYPE'] = facility_summary['PRES_FACILITY_TYPE'].astype('str')
facility_summary['PRES_FACILITY_OVERALL_TYPE'] = facility_summary['PRES_FACILITY_OVERALL_TYPE'].astype('str')

idxs = []
for i in facility_summary.index:
    if 'Wastewater' in facility_summary.loc[i, 'PRES_FACILITY_OVERALL_TYPE']:
        for x in facility_types:
            if x in facility_summary.loc[i, 'PRES_FACILITY_TYPE']:
                idxs.append(i)
                break
facility_summary = facility_summary.loc[idxs]
facility_summary.reset_index(inplace = True, drop = True)

# Merge with information about the population receiving collection at each facility

population = pd.read_csv('../data/epa/SUMMARY_POPULATION.csv')
population = population[['CWNS_NUMBER', 
                         'PRES_RES_RECEIVING_COLLCTN', 
                         'PRES_N_RES_RECEIVING_COLLCTN']]

facilities = facility_summary.merge(population, on = 'CWNS_NUMBER', how = 'left')

# Aggregate population size receiving collection by state and primary county

states = []
counties = []
pop_res = []
pop_n_res = []
for name, df in facilities.groupby(['STATE', 'PRIMARY_COUNTY']):
    states.append(name[0])
    counties.append(name[1])
    pop_res.append(df['PRES_RES_RECEIVING_COLLCTN'].sum())
    pop_n_res.append(df['PRES_N_RES_RECEIVING_COLLCTN'].sum())

county_collections = pd.DataFrame({'STATE':states, 
             'COUNTY':counties, 
             'PRES_RES_RECEIVING_COLLCTN':pop_res,
             'PRES_N_RES_RECEIVING_COLLCTN':pop_n_res})

# Import US counties shapefile and state fips codes

# Also do this for county fips codes

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

# Inconsistencies in using spaces and accents in county names
# In all cases, favor the census shapefile nomenclature

# EPA data has La Salle, IL whereas census shapefile has LaSalle, IL
idx = np.where((county_collections['STATE']=='IL')&(county_collections['COUNTY']=='La Salle'))[0][0]
county_collections.at[idx,'COUNTY']='LaSalle'

# EPA data has De Kalb, IN whereas census shapefile has DeKalb, IN
idx = np.where((county_collections['STATE']=='IN')&(county_collections['COUNTY']=='De Kalb'))[0][0]
county_collections.at[idx,'COUNTY']='DeKalb'

# EPA data has La Porte, IN whereas census shapefile has LaPorte, IN
idx = np.where((county_collections['STATE']=='IN')&(county_collections['COUNTY']=='La Porte'))[0][0]
county_collections.at[idx,'COUNTY']='LaPorte'

# EPA data has Lagrange, IN whereas census shapefile has LaGrange, IN
idx = np.where((county_collections['STATE']=='IN')&(county_collections['COUNTY']=='Lagrange'))[0][0]
county_collections.at[idx,'COUNTY']='LaGrange'

idx = np.where((county_collections['STATE']=='LA')&(county_collections['COUNTY']=='La Salle'))[0][0]
county_collections.at[idx,'COUNTY']='LaSalle'

idx = np.where((county_collections['STATE']=='NM')&(county_collections['COUNTY']=='DeBaca'))[0][0]
county_collections.at[idx,'COUNTY']='De Baca'

idx = np.where((county_collections['STATE']=='NM')&(county_collections['COUNTY']=='Dona Ana'))[0][0]
county_collections.at[idx,'COUNTY']='Doña Ana'

idx = np.where((county_collections['STATE']=='PA')&(county_collections['COUNTY']=='Mc Kean'))[0][0]
county_collections.at[idx,'COUNTY']='McKean'

# Puerto Rico names that were missing the accents
pr_county_accents = ['Cataño',
'Comerío',
'Guánica',
'Las Marías',
'Loíza',
'Mayagüez',
'Peñuelas',
'San Germán',
'San Sebastián']

for pr_county_accent in pr_county_accents:
    idx = np.where((county_collections['STATE']=='PR')&(county_collections['COUNTY']==unidecode(pr_county_accent)))[0][0]
    county_collections.at[idx,'COUNTY']=pr_county_accent
    
# Checked that all counties represented in the EPA data are merged to a corresponding county in the census shapefile

county_summary = shapefile.merge(county_collections, on = ['STATE', 'COUNTY'], how = 'outer')

# Counties only found in the census shapefile indicate a population of 0 receiving collection
# Add flag that there was no data in the epa dataset
county_summary['epa_data']=True
county_summary.loc[np.isnan(county_summary['PRES_RES_RECEIVING_COLLCTN']),'epa_data']=False
county_summary['PRES_RES_RECEIVING_COLLCTN'].fillna(0, inplace = True)
county_summary['PRES_N_RES_RECEIVING_COLLCTN'].fillna(0, inplace = True)

# Merge with CBSA data of metro/micro/rural

county2cbsa = pd.read_csv('../data/geography_files/county_to_cbsa_reformatted.csv')
county2cbsa = county2cbsa[1:]
county2cbsa.reset_index(inplace = True, drop = True)
county2cbsa.reset_index(inplace = True, drop = True)
county2cbsa = county2cbsa[['CBSA Code', 'CBSA Title', 'Metropolitan/Micropolitan Statistical Area', 'FIPS State Code', 'FIPS County Code', 'Central/Outlying County']]
county2cbsa.rename({'CBSA Code':'cbsa_fips', 'CBSA Title':'cbsa_name', 'Metropolitan/Micropolitan Statistical Area':'metro_micro','FIPS State Code':'STATEFP', 'FIPS County Code':'COUNTYFP', 'Central/Outlying County':'central_outlying_county'}, inplace = True, axis = 'columns')

county_summary = county_summary.merge(county2cbsa, on = ['STATEFP','COUNTYFP'], how = 'left')#, indicator = True)
county_summary['metro_micro'].fillna('Rural Area', inplace = True)

# Checked that all counties in count2cbsa file were found in the county_summary

county_summary.drop('geometry', axis = 'columns', inplace = True)
county_summary.to_csv('../outputs/epa_sewer_connectivity_by_county.csv')