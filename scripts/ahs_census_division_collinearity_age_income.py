import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

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

# Clearn up columns
geo_type = 'DIVISION'
ahs = fnc.cleanup_column(ahs, geo_type, ahsdict)
geo_labels = fnc.get_labels(labels, geo_type)

var1 = 'HHAGE' # Householder age
var2 = 'PERPOVLVL' # Household income as percentage of poverty level
ahs = fnc.cleanup_column(ahs, var1, ahsdict)
ahs = fnc.cleanup_column(ahs, var2, ahsdict)

# Remove households that had "not applicable" entry for these variables
ahs_numerical = ahs[(ahs[var1]!='Not applicable')&(ahs[var2]!='Not applicable')]
ahs_numerical.loc[:,var1] = ahs_numerical[var1].astype('float')
ahs_numerical.loc[:,var2] = ahs_numerical[var2].astype('float')

# Loop through all values of the geographical variable
fig, ax = plt.subplots(3,3, figsize = (9,9), sharex = True, sharey = True)
i = 0
j = 0
for value, df in ahs_numerical.groupby(geo_type):
    df_base = ahs_numerical[ahs_numerical[geo_type]==value]
    pearsonr = scipy.stats.pearsonr(df_base[var1], df_base[var2])[0]
    pvalue = scipy.stats.pearsonr(df_base[var1], df_base[var2])[1]
    sns.regplot(ax = ax[i,j], data=df_base, x=var1, y=var2, marker = '.', scatter_kws = {'alpha':0.2, 'color':'gray'})
    ax[i,j].set_title(geo_labels[geo_labels['Value'].values==value]['Label'].values[0] + '\nPearson r='+str(round(pearsonr,2)))
    ax[i,j].set_xlabel('')
    ax[i,j].set_ylabel('')
    
    if j == 2:
        i+=1
        j=0
    else:
        j+=1
        
fig.supxlabel('Householder age')
fig.supylabel('Household income as percent of poverty threshold')
plt.tight_layout()
plt.savefig('../figures/figsi_collinearity_age_income.png', dpi = 300)
plt.savefig('../figures/figsi_collinearity_age_income.pdf')