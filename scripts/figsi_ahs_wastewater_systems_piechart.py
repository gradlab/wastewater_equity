import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import binom, ttest_1samp
from scipy.integrate import cumtrapz
import geopandas as gpd
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)
import ahs_2019_2021_functions as fnc

# Load data
ahsn = pd.read_csv('../data/ahs/puf_national_household_2021_v1.0.csv')
labels = pd.read_csv('../data/ahs/value_labels_2021.csv')
ahsdict = pd.read_csv('../data/ahs/ahsdict_2019_2021_04OCT22_10_42_49_75_2021.csv')

#Plots a summary pie chart for weighted counts of categorical variables
ahsn = fnc.cleanup_column(ahsn, 'SEWTYPE', ahsdict)

cat_var = 'SEWTYPE'
fig = plt.figure()

values = fnc.get_labels(labels, cat_var)['Value'].values
weighted_counts = fnc.get_weighted_counts(ahsn, cat_var, values)
total_weighted_households = np.sum(weighted_counts)

frac = weighted_counts/total_weighted_households

frac = frac[frac>0.05]
frac = np.append(frac, 1-np.sum(np.array(frac)))
pie_labels = ['Public sewer', 'Standard septic tank', 'Other']
plt.pie(frac, labels = pie_labels, autopct='%1.1f%%')

plt.savefig('../figures/figsi_ahs_wastewater_systems_piechart.png')
plt.savefig('../figures/figsi_ahs_wastewater_systems_piechart.pdf')
