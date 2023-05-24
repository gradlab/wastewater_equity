import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import seaborn as sns
from scipy.stats import pearsonr
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Load data

merged = pd.read_csv('../outputs/utah_sewer_connectivity.csv')

# Make plot

var_dict = {'DP05_0037PE':'Percent one race and \nwhite',
             'DP05_0038PE':'Percent one race and \nblack or african american',
             'DP05_0039PE':'Percent one race and \namerican indian and alaska native',
             'DP05_0044PE':'Percent one race and \nasian',
             'DP05_0052PE':'Percent one race and \nnative hawaiian and other pacific islander',
             'DP05_0057PE':'Percent one race and \nsome other race',
            'DP05_0071PE':'Percent hispanic',
            'DP03_0062E':'Median household income',
            'DP05_0018E':'Median age',
            'DP02_0016E':'Average household size',
            'DP03_0096PE':'Percent with health insurance coverage'}

num_households_var = 'DP02_0001E'

plt.figure(figsize = (10,12))
i = 1
for var in var_dict:
    ax = plt.subplot(4,3,i)
    sns.scatterplot(ax = ax, data = merged, x = 'frac_collection', y = var, marker = '.')
    sns.regplot(ax = ax, data = merged, x = 'frac_collection', y = var)
    merged_finite = merged[(np.isfinite(merged['frac_collection']))&(~np.isnan(merged[var]))]
    ax.set_title('Pearson r = ' + str(round(pearsonr(merged_finite['frac_collection'], merged_finite[var])[0],5)) +
                 '\nq value = ' + str(round(pearsonr(merged_finite['frac_collection'], merged_finite[var])[1]*len(var_dict), 5)))

    ax.set_ylabel(var_dict[var])
    ax.set_xlabel('Fraction of county subdivision \nreceiving collection')
    i+=1
plt.suptitle('All county subdivisions')
plt.tight_layout()
plt.savefig('../figures/figsi_utah_sewer_connectivity_correlation.png')
plt.savefig('../figures/figsi_utah_sewer_connectivity_correlation.pdf')