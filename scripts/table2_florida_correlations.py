import pandas as pd
import numpy as np
import math
from scipy.stats import pearsonr, ttest_ind

# Load data
septic_tanks = pd.read_csv('../outputs/florida_septic_inspections_by_county_subdivision_census.csv', index_col = 0)
merged = septic_tanks.copy()

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

var_all = []
pearsonrs = []
ps = []
qs = []

for var in var_dict:
    merged_finite = merged[(np.isfinite(merged['percentage_not_septic']))&(~np.isnan(merged[var]))]

    var_all.append(var_dict[var])
    pearsonrs.append(pearsonr(merged_finite['percentage_not_septic'], merged_finite[var])[0])
    ps.append(pearsonr(merged_finite['percentage_not_septic'], merged_finite[var])[1])
    qs.append(pearsonr(merged_finite['percentage_not_septic'], merged_finite[var])[1]*len(var_dict))
septic_var_corr = pd.DataFrame({'variable':var_all, 'pearsonr':pearsonrs, 'pvalue':ps, 'qvalue':qs})
septic_var_corr.sort_values('qvalue', inplace = True)
septic_var_corr.reset_index(drop = True, inplace = True)
septic_var_corr.to_csv('../outputs/table2_florida_correlations.csv')