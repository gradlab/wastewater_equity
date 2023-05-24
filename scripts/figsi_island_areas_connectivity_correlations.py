import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from scipy.stats import pearsonr
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

def calculate_correlations(merged, output_filename, var_dict):

    var_all = []
    pearsonrs = []
    ps = []
    qs = []

    for var in var_dict:
        merged_finite = merged[(np.isfinite(merged['frac_sewer']))&(~np.isnan(merged[var]))]

        var_all.append(var_dict[var])
        pearsonrs.append(pearsonr(merged_finite['frac_sewer'], merged_finite[var])[0])
        ps.append(pearsonr(merged_finite['frac_sewer'], merged_finite[var])[1])
        qs.append(pearsonr(merged_finite['frac_sewer'], merged_finite[var])[1]*len(var_dict))
    sewer_var_corr = pd.DataFrame({'variable':var_all, 'pearsonr':pearsonrs, 'pvalue':ps, 'qvalue':qs})
    sewer_var_corr.sort_values('qvalue', inplace = True)
    sewer_var_corr.reset_index(drop = True, inplace = True)
    sewer_var_corr.to_csv(output_filename)

def plot_correlations(merged, figure_filename_no_suffix, var_dict):
    plt.figure(figsize = (10,12))
    i = 1
    for var in var_dict:
        ax = plt.subplot(4,3,i)
        sns.scatterplot(ax = ax, data = merged, x = 'frac_sewer', y = var, marker = '.')
        sns.regplot(ax = ax, data = merged, x = 'frac_sewer', y = var)
        merged_finite = merged[(np.isfinite(merged['frac_sewer']))&(~np.isnan(merged[var]))]
        ax.set_title('Pearson r = ' + str(round(pearsonr(merged_finite['frac_sewer'], merged_finite[var])[0],5)) +
                     '\nq value = ' + str(round(pearsonr(merged_finite['frac_sewer'], merged_finite[var])[1]*len(var_dict), 5)))

        ax.set_ylabel(var_dict[var])
        ax.set_xlabel('Fraction of CDP on sewer')
        i+=1
    plt.suptitle('All CDPs')
    plt.tight_layout()
    plt.savefig(figure_filename_no_suffix + '.png')
    plt.savefig(figure_filename_no_suffix + '.pdf')
    
def run_main(data_filename, table_filename, figure_filename_no_suffix, var_dict):
    merged = pd.read_csv(data_filename, index_col = 0)
    calculate_correlations(merged, table_filename, var_dict)
    plot_correlations(merged, figure_filename_no_suffix, var_dict)

# American Samoa
var_dict = {'DP1_0095P':'Percent one race and \nWhite',
             'DP1_0096P':'Percent one race and \nBlack or African American',
             'DP1_0097P':'Percent one race and \nAmerican Indian and Alaska Native',
             'DP1_0086P':'Percent one race and \nAsian',
             'DP1_0078P':'Percent one race and \nNative Hawaiian and Other Pacific Islander',
             'DP1_0098P':'Percent one race and \nsome other race', 
            'DP1_0105P':'Percent Hispanic',
            'DP3_0104C':'Median income',
            'DP1_0073C':'Median age',
            'DP4_0004C':'Average household size',
            'DP3_0065P':'Percent with health insurance coverage'}

data_filename = '../outputs/island_areas_sewer_connectivity_american_samoa.csv'
table_filename = '../outputs/island_areas_sewer_connectivity_correlations_american_samoa.csv'
figure_filename_no_suffix = '../figures/figsi_island_areas_connectivity_correlation_american_samoa'
run_main(data_filename, table_filename, figure_filename_no_suffix, var_dict)

# Guam
var_dict = {'DP1_0094P':'Percent one race and \nWhite',
             'DP1_0078P':'Percent one race and \nBlack or African American',
             'DP1_0096P':'Percent one race and \nAmerican Indian and Alaska Native',
             'DP1_0095P':'Percent one race and \nAsian',
             'DP1_0097P':'Percent one race and \nNative Hawaiian and Other Pacific Islander',
             'DP1_0098P':'Percent one race and \nsome other race', 
            'DP1_0110P':'Percent Hispanic',
            'DP3_0104C':'Median income',
            'DP1_0073C':'Median age',
            'DP4_0004C':'Average household size',
            'DP3_0065P':'Percent with health insurance coverage'}

data_filename = '../outputs/island_areas_sewer_connectivity_guam.csv'
table_filename = '../outputs/island_areas_sewer_connectivity_correlations_guam.csv'
figure_filename_no_suffix = '../figures/figsi_island_areas_connectivity_correlation_guam'
run_main(data_filename, table_filename, figure_filename_no_suffix, var_dict)

# Northern Mariana Islands
var_dict = {'DP1_0097P':'Percent one race and \nWhite',
             'DP1_0098P':'Percent one race and \nBlack or African American',
             'DP1_0099P':'Percent one race and \nAmerican Indian and Alaska Native',
             'DP1_0078P':'Percent one race and \nAsian',
             'DP1_0087P':'Percent one race and \nNative Hawaiian and other Pacific Islander',
             'DP1_0100P':'Percent one race and \nsome other race', 
            'DP1_0108P':'Percent Hispanic',
            'DP3_0104C':'Median income',
            'DP1_0073C':'Median age',
            'DP4_0004C':'Average household size',
            'DP3_0065P':'Percent with health insurance coverage'}

data_filename = '../outputs/island_areas_sewer_connectivity_northern_mariana_islands.csv'
table_filename = '../outputs/island_areas_sewer_connectivity_correlations_northern_mariana_islands.csv'
figure_filename_no_suffix = '../figures/figsi_island_areas_connectivity_correlation_northern_mariana_islands'
run_main(data_filename, table_filename, figure_filename_no_suffix, var_dict)

# Virgin Islands
var_dict = {'DP1_0094P':'Percent one race and \nWhite',
             'DP1_0078P':'Percent one race and \nBlack or African American',
             'DP1_0096P':'Percent one race and \nAmerican Indian and Alaska Aative',
             'DP1_0095P':'Percent one race and \nAsian',
             'DP1_0097P':'Percent one race and \nNative Hawaiian and Other Pacific Islander',
             'DP1_0098P':'Percent one race and \nsome other race', 
            'DP1_0105P':'Percent Hispanic',
            'DP3_0104C':'Median income',
            'DP1_0073C':'Median age',
            'DP4_0004C':'Average household size',
            'DP3_0065P':'Percent with health insurance coverage'}

data_filename = '../outputs/island_areas_sewer_connectivity_virgin_islands.csv'
table_filename = '../outputs/island_areas_sewer_connectivity_correlations_virgin_islands.csv'
figure_filename_no_suffix = '../figures/figsi_island_areas_connectivity_correlation_virgin_islands'
run_main(data_filename, table_filename, figure_filename_no_suffix, var_dict)