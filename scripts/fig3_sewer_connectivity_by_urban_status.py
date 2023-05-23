import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Load percent sewered output from ahs_census_division.py

percent_sewered_df = pd.read_csv('../outputs/ahs_sewer_connectivity_by_urban_status.csv', index_col = 0)

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
        'variable_values':['18', '30', '40', '50', '65', '75'],
        'variable_descriptions':['18-29', '30-39', '40-49', '50-64', '65-74', '75+']
    },
    {
        'variable_type':'POOR',
        'variable_type_description':'Poverty level',
        'variable_values':['0', '100'],
        'variable_descriptions':['In poverty', 'Not in poverty']
    },
    {
        'variable_type':'PER',
        'variable_type_description':'Household size',
        'variable_values':['1', '2', '3', '4'],
        'variable_descriptions':['1', '2', '3', '4+']
    }
]

# Make plot

fig, ax = plt.subplots(6,1, figsize = (8,13), sharex = True, gridspec_kw = {'wspace':0})

percent_sewered_df_overall_sorted = percent_sewered_df[percent_sewered_df['variable_type']=='overall'].sort_values('percent_sewered', ascending = False)

# Get the order of the locations (in this case ordered from highest connectivity to lowest connectivity)
geo_values = percent_sewered_df_overall_sorted['geo_value'].values
geo_descriptions = percent_sewered_df_overall_sorted['geo_description'].values
x = np.array(range(len(geo_values)))
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:cyan', 'tab:red', 'tab:purple']

i=0
# Loop through variables
for variable in variables:
    variable_type = variable['variable_type']
    variable_type_description = variable['variable_type_description']
    variable_values = variable['variable_values']
    variable_descriptions = variable['variable_descriptions']
    percent_sewered_df_variable = percent_sewered_df[percent_sewered_df['variable_type']==variable_type]
    p=[]
    max_abs_value = 0
    for k in x:
        geo_value = geo_values[k]
        # Overall
        if variable_type=='overall':
            row = percent_sewered_df_variable.loc[percent_sewered_df_variable['geo_value']==geo_value]
            y = row['percent_sewered'].values[0]
            yerr_lower = y - row['percent_sewered_lower'].values[0]
            yerr_upper = row['percent_sewered_upper'].values[0] - y
            ax[i].bar(k*8, y, yerr = [[yerr_lower], [yerr_upper]], width = 4, color = 'gray', capsize = 1)

        # Demographic and economic variables
        else:
            j=0
            num_values = len(variable_values)
            width = 6/num_values
            for variable_value in variable_values:
                row = percent_sewered_df_variable.loc[(percent_sewered_df_variable['geo_value']==geo_value)&(percent_sewered_df_variable['variable_value']==variable_value)]
                row_overall = percent_sewered_df_overall_sorted[percent_sewered_df_overall_sorted['geo_value']==geo_value]

                color = colors[j]
                
                # Note that we just use the errors on the group in question, 
                # and don't propagate the errors from the overall estimate 
                # because those error bars are small and propagating 
                # asymmetric 95% CIs is tricky
                
                y = row['percent_sewered'].values[0]
                y_overall = row_overall['percent_sewered'].values[0]
                
                yerr_lower = y - row['percent_sewered_lower'].values[0]
                yerr_upper = row['percent_sewered_upper'].values[0] - y
                dely = y-y_overall
                
                if yerr_lower<0:
                    yerr_lower=0
                if yerr_upper<0:
                    yerr_upper=0
                max_abs_value = np.max(np.array([max_abs_value, np.abs(dely-yerr_lower), np.abs(dely+yerr_upper)]))
                
                p1 = ax[i].bar(k*8-round(len(variable_values)/2)+j*width, dely, yerr = [[yerr_lower], [yerr_upper]], width = width, color = color, error_kw = {'lw':0.5}, capsize = 0.5)
                ax[i].plot([k*8-4, k*8-4], [-70, 70], linestyle = ':', color = 'k', linewidth = 0.5, alpha = 0.5)
                
                j+=1
                if k==0:
                    # Only display legend once (not for every location)
                    p.append(p1)
        k+=1
    
    # Make the plot pretty
    if variable_type=='overall':
        ax[i].set_ylim([0, 100])
        ax[i].set_ylabel('% of households \nconnected to sewer')
        # ax[i].text(-3, 85, variable_type_description)
    else:
        ax[i].plot([x[0]-4, 8*x[-1]+4], [0, 0], 'k-', linewidth = 0.5)
        ax[i].set_ylim([-1.1*max_abs_value, 1.1*max_abs_value])
        ax[i].plot([k*8-4, k*8-4], [-1.1*max_abs_value, 1.1*max_abs_value], linestyle = ':', color = 'lightgrey', linewidth = 0.5)
        # ax[i].text(-3, 0.8*max_abs_value, variable_type_description)
        ax[i].legend(p, variable_descriptions, loc = (1.01, 0),  fontsize = 10)
        
    ax[i].set_title(variable_type_description)
    ax[i].set_xticks(x*8)
    ax[i].set_xticklabels(geo_descriptions, rotation = 90)
    ax[i].set_xlim([x[0]-4, x[-1]*8+4])
    
    i+=1
ax[3].set_ylabel('% of households connected to sewer - \n% of households connected to sewer in census division')
fig.suptitle('By central city/suburban status (2013)')
plt.tight_layout()
plt.savefig('../figures/fig3_sewer_connectivity_by_urban_status.png', dpi = 300)
plt.savefig('../figures/fig3_sewer_connectivity_by_urban_status.pdf', dpi = 300)