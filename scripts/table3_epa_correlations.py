import pandas as pd
import numpy as np
import math
from scipy.stats import pearsonr

merged = pd.read_csv('../outputs/epa_sewer_connectivity_by_county_census.csv', index_col = 0)

states = ['NY',
          'CA',
          'FL',
          'NJ',
          'MD',
          'IA',
          'MN',
          'MI']

var_dict = {'DP05_0032PE':'Percent one race and white',
             'DP05_0033PE':'Percent one race and black or african american',
             'DP05_0034PE':'Percent one race and american indian and alaska native',
             'DP05_0039PE':'Percent one race and asian',
             'DP05_0047PE':'Percent one race and native hawaiian and other pacific islander',
             'DP05_0052PE':'Percent one race and some other race',
            'DP05_0066PE':'Percent hispanic',
           'S1903_C02_001E':'Median income',
           'DP05_0017E':'Median age',
           'S1101_C01_002E':'Average household size',
           'S2701_C03_001E':'Percent uninsured'}
    
var_all = []
pearsonrs = []
ps = []
qs = []
states_list = []
for state in states:
    merged_state = merged[merged['STATE']==state]

    for var in var_dict:
        merged_finite = merged_state[(np.isfinite(merged_state['frac_pres_res_collection']))&(~np.isnan(merged_state[var]))]

        var_all.append(var_dict[var])
        pearsonrs.append(pearsonr(merged_finite['frac_pres_res_collection'], merged_finite[var])[0])
        ps.append(pearsonr(merged_finite['frac_pres_res_collection'], merged_finite[var])[1])
        qs.append(pearsonr(merged_finite['frac_pres_res_collection'], merged_finite[var])[1]*len(var_dict)*len(states))
        states_list.append(state)
sewer_var_corr = pd.DataFrame({'variable':var_all, 'state':states_list, 'pearsonr':pearsonrs, 'pvalue':ps, 'qvalue':qs})
sewer_var_corr.sort_values('qvalue', inplace = True)
sewer_var_corr.reset_index(drop = True, inplace = True)
sewer_var_corr.to_csv('../outputs/table3_epa_correlations.csv')