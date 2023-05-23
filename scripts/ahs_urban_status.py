import pandas as pd
import numpy as np
from scipy.stats import binom, ttest_1samp
from scipy.integrate import cumtrapz

import ahs_2013_functions as fnc

# Load data

ahs = pd.read_csv('../data/ahs/puf_national_household_2013_v2.0.csv')

labels = pd.read_csv('../data/ahs/value_labels_national_2013.csv')
ahsdict = pd.read_csv('../data/ahs/ahsdict_2013_23JAN23_11_43_08_06.csv')

ahs = fnc.cleanup_column(ahs, 'SEWDIS', ahsdict)

# Making the assumption that since there is no option for public sewer and the majority of people have chosen the option of "not applicable" that this corresponds to the public sewer option

sewtype_summary = np.empty(len(ahs)).astype('str')
for i in range(len(ahs['SEWDIS'])):
    if ahs.loc[i, 'SEWDIS'] == 'N':
        sewtype_summary[i] = 'Public sewer'
    elif ahs.loc[i, 'SEWDIS'] == '1':
        sewtype_summary[i] = 'Septic tank or cesspool'
    else:
        sewtype_summary[i] = 'Other'
ahs['SEWTYPE_summary'] = sewtype_summary

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
        'variable_type':'POOR',
        'variable_type_description':'Poverty level',
        'variable_values':[0, 100],
        'variable_descriptions':['In poverty', 'Not in poverty']
    },
    {
        'variable_type':'PER',
        'variable_type_description':'Household size',
        'variable_values':[1, 2, 3, 4],
        'variable_descriptions':['1', '2', '3', '4+']
    }
]

# 2013 Central city / suburban status (METRO3)

geo_type = 'METRO3'
ahs = fnc.cleanup_column(ahs, geo_type, ahsdict)

percent_sewered_df = pd.DataFrame()

for variable in variables:
    variable_type = variable['variable_type']
    variable_type_description = variable['variable_type_description']
    variable_values = variable['variable_values']
    variable_descriptions = variable['variable_descriptions']
    variable_class = fnc.get_labels(labels, geo_type)['Type'].values[0]

    if variable_type=='overall':
        percent_sewered_df = pd.concat([percent_sewered_df,fnc.get_percent_sewered_overall(ahs, geo_type, labels)])
    else:
        ahs = fnc.cleanup_column(ahs, variable_type, ahsdict)
        percent_sewered_df = pd.concat([percent_sewered_df,fnc.get_percent_sewered(ahs, geo_type, ahsdict, labels, variable_type, variable_type_description, variable_values, variable_descriptions)])
        
# Save results
percent_sewered_df.to_csv('../outputs/ahs_sewer_connectivity_by_urban_status.csv')