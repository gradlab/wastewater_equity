import pandas as pd
import numpy as np
import math
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, ttest_ind
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Plot SI figs of correlations between percentage of county subdivision not on septic and various demographic and economic variables

# Uses output of florida_septic_analysis.py

def plot_correlations(df, output_filename_no_suffix, var_dict, title):
    plt.figure(figsize = (10,12))
    i = 1
    for var in var_dict:
        ax = plt.subplot(4,3,i)
        sns.scatterplot(ax = ax, data = df, x = 'percentage_not_septic', y = var, marker = '.')
        sns.regplot(ax = ax, data = df, x = 'percentage_not_septic', y = var, marker = '.')
        df_finite = df[(np.isfinite(df['frac_septic']))&(~np.isnan(df[var]))]
        ax.set_title('Pearson r = ' + str(round(pearsonr(df_finite['percentage_not_septic'], df_finite[var])[0],2)) +
                     '\nq value = ' + "{:.1E}".format(pearsonr(df_finite['percentage_not_septic'], df_finite[var])[1]*len(var_dict)))

        ax.set_ylabel(var_dict[var])
        ax.set_xlabel('% of county subdivision not on septic')
        i+=1
    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(output_filename_no_suffix + '.png')
    plt.savefig(output_filename_no_suffix + '.pdf')

# Load data
septic_tanks = pd.read_csv('../outputs/florida_septic_inspections_by_county_subdivision_census.csv', index_col = 0)

var_dict = {'DP05_0032PE':'Percent one race and \nWhite',
             'DP05_0033PE':'Percent one race and \nBlack or African American',
             'DP05_0034PE':'Percent one race and \nAmerican Indian and Alaska Native',
             'DP05_0039PE':'Percent one race and \nAsian',
             'DP05_0047PE':'Percent one race and \nNative Hawaiian and Other Pacific Islander',
             'DP05_0052PE':'Percent one race and \nSome other race',
            'DP05_0066PE':'Percent Hispanic',
            'S1903_C02_001E':'Median income',
            'DP05_0017E':'Median age',
            'S1101_C01_002E':'Average household size',
            'S2701_C03_001E':'Percent uninsured'}

# Include all county subdivisions

title = 'All county subdivisions'
output_filename_no_suffix = '../figures/figsi_florida_correlations'
plot_correlations(septic_tanks, output_filename_no_suffix, var_dict, title)

# Metropolitan county subdivisions
df = septic_tanks[septic_tanks['metro_micro']=='Metropolitan Statistical Area']
title = 'County subdivisions in metropolitan statistical areas'
output_filename_no_suffix = '../figures/figsi_florida_correlations_metro'
plot_correlations(df, output_filename_no_suffix, var_dict, title)

# Micropolitan county subdivisions
df = septic_tanks[septic_tanks['metro_micro']=='Micropolitan Statistical Area']
title = 'County subdivisions in micropolitan statistical areas'
output_filename_no_suffix = '../figures/figsi_florida_correlations_micro'
plot_correlations(df, output_filename_no_suffix, var_dict, title)

# Rural county subdivisions
df = septic_tanks[septic_tanks['metro_micro']=='Rural Area']
title = 'County subdivisions in rural areas'
output_filename_no_suffix = '../figures/figsi_florida_correlations_rural'
plot_correlations(df, output_filename_no_suffix, var_dict, title)
