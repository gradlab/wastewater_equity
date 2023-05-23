import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Load data
merged = pd.read_csv('../outputs/epa_sewer_connectivity_by_county_census.csv', index_col = 0)

cbsa_top35_metro = pd.read_csv('../outputs/ahs_sewer_connectivity_by_cbsa_for_epa_comparison.csv', index_col = 0)
cbsa_top35_metro['ahs_frac_sewered']=cbsa_top35_metro['percent_sewered']/100
cbsa_top35_metro['ahs_frac_sewered_lower']=cbsa_top35_metro['percent_sewered_lower']/100
cbsa_top35_metro['ahs_frac_sewered_upper']=cbsa_top35_metro['percent_sewered_upper']/100

print(cbsa_top35_metro)
merged_metro = merged[merged['cbsa_fips'].isin(cbsa_top35_metro['cbsa_fips'])].reset_index(drop = True)

cbsas = []
cbsa_names = []
frac_pres_res_collection = []
for cbsa, df in merged_metro.groupby('cbsa_fips'):
    cbsas.append(cbsa)
    cbsa_names.append(df['cbsa_name'].values[0])
    frac_pres_res_collection.append(df['PRES_RES_RECEIVING_COLLCTN'].sum()/df['DP05_0001E'].sum())
cbsa_connection = pd.DataFrame({'cbsa_fips':cbsas, 'cbsa_name':cbsa_names, 'epa_frac_pres_res_collection':frac_pres_res_collection})

compare_ahs_epa = cbsa_connection.merge(cbsa_top35_metro, on = ['cbsa_fips', 'cbsa_name'])

# Filtering by only the states where there was high investment in data collection
cbsa_fips_to_compare = [35620.0,
                       40380.0,
                       31080.0,
                       40140.0,
                       41860.0,
                       41940.0,
                       33100.0,
                       45300.0,
                       12580.0,
                        37980.0,
                       47900.0,
                       33460.0,
                       19820.0,]
compare_ahs_epa_filtered = compare_ahs_epa[compare_ahs_epa['cbsa_fips'].isin(cbsa_fips_to_compare)]

# Calculate correlation
print(compare_ahs_epa.columns)
print(cbsa_connection.columns)
print(cbsa_top35_metro.columns)

pearson_test = pearsonr(compare_ahs_epa_filtered['ahs_frac_sewered'], compare_ahs_epa_filtered['epa_frac_pres_res_collection'])
pearsonr_value = pearson_test[0]
pvalue = pearson_test[1]

# Plot
plt.figure(figsize = (4,4))
plt.errorbar(compare_ahs_epa_filtered['ahs_frac_sewered'], compare_ahs_epa_filtered['epa_frac_pres_res_collection'], xerr = [compare_ahs_epa_filtered['ahs_frac_sewered']-compare_ahs_epa_filtered['ahs_frac_sewered_lower'], compare_ahs_epa_filtered['ahs_frac_sewered_upper']-compare_ahs_epa_filtered['ahs_frac_sewered']], linestyle = '', marker = '.')
plt.plot([0.4,1], [0.4,1], 'k--')
plt.xlabel('AHS Fraction of households on sewer')
plt.ylabel('EPA CWNS \nFraction of residents receiving collection')
plt.title('Metropolitan CBSAs')
plt.text(0.4, 1.2, 'Pearson r = '+ str(round(pearsonr_value,2)) + '\np-value = ' + str(round(pvalue,3)))
plt.tight_layout()
plt.savefig('../figures/figsi_compare_ahs_epa.png')
plt.savefig('../figures/figsi_compare_ahs_epa.pdf')