import pandas as pd
import numpy as np
from scipy.stats import binom, ttest_1samp
from scipy.integrate import cumtrapz

import ahs_2019_2021_functions as fnc

# Load data

ahsn = pd.read_csv('../data/ahs/puf_national_household_2021_v1.0.csv')

labels = pd.read_csv('../data/ahs/value_labels_2021.csv')
ahsdict = pd.read_csv('../data/ahs/ahsdict_2019_2021_04OCT22_10_42_49_75_2021.csv')

ahsn = fnc.cleanup_column(ahsn, 'SEWTYPE', ahsdict)

# Summarize sewer data into public sewer, not public sewer, or not reported

sewtype_summary = np.empty(len(ahsn)).astype('str')
for i in range(len(ahsn['SEWTYPE'])):
    if ahsn.loc[i, 'SEWTYPE'] == '01':
        sewtype_summary[i] = 'Public sewer'
    elif ahsn.loc[i, 'SEWTYPE'] == 'M':
        sewtype_summary[i] = 'Not reported'
    else:
        sewtype_summary[i] = 'Not public sewer'
ahsn['SEWTYPE_summary'] = sewtype_summary

ahs = ahsn.copy()

# Define variables of interest

variables=[
    {
        'variable_type':'overall',
        'variable_type_description':'Overall',
        'variable_values':'overall',
        'variable_descriptions':'overall'
    },
    {
        'variable_type':'HHRACE',
        'variable_type_description':'Householder race (one race)',
        'variable_values':['01', '02', '03', '04', '05'],
        'variable_descriptions':['White', 'Black or African American', 'American Indian and Alaska Native', 'Asian', 'Native Hawaiian and Other Pacific Islander']
    },
    {
        'variable_type':'HHSPAN',
        'variable_type_description':'Householder Hispanic',
        'variable_values':['1', '2'],
        'variable_descriptions':['Hispanic', 'Not Hispanic']
    },
    {
        'variable_type':'HHAGE',
        'variable_type_description':'Householder age',
        'variable_values':[18, 30, 40, 50, 65, 75],
        'variable_descriptions':['18-29', '30-39', '40-49', '50-64', '65-74', '75+']
    },
    {
        'variable_type':'PERPOVLVL',
        'variable_type_description':'Poverty level',
        'variable_values':[0, 100],
        'variable_descriptions':['In poverty', 'Not in poverty']
    },
    {
        'variable_type':'NUMPEOPLE',
        'variable_type_description':'Household size',
        'variable_values':[1, 2, 3, 4],
        'variable_descriptions':['1', '2', '3', '4+']
    }
]

# Calculate summary stats
geo_type = 'DIVISION'
ahs = fnc.cleanup_column(ahs, geo_type, ahsdict)

percent_sewered_df = pd.DataFrame()

for variable in variables:
    variable_type = variable['variable_type']
    variable_type_description = variable['variable_type_description']
    variable_values = variable['variable_values']
    variable_descriptions = variable['variable_descriptions']
    variable_class = fnc.get_labels(labels, geo_type)['Type'].values[0]

    if variable_type=='overall':
        percent_sewered_df = pd.concat([percent_sewered_df, fnc.get_percent_sewered_overall(ahs, geo_type, labels)])
    else:
        ahs = fnc.cleanup_column(ahs, variable_type, ahsdict)
        percent_sewered_df = pd.concat([percent_sewered_df, fnc.get_percent_sewered(ahs, geo_type, ahsdict, labels, variable_type, variable_type_description, variable_values, variable_descriptions)])

# Save results
percent_sewered_df.to_csv('../outputs/ahs_sewer_connectivity_by_census_division.csv')

# Print some summary stats
for variable_type in np.unique(percent_sewered_df['variable_type']):
    print(variable_type)
    for value, df in percent_sewered_df[percent_sewered_df['variable_type']==variable_type].groupby('variable_description'):
        print('\t', value, ', point estimate:', round(np.mean(df['percent_sewered']),1), ', delta:', round(np.mean(df['percent_sewered_delta']),1))