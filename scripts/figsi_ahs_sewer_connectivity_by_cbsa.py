import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import matplotlib
font = {'family':'arial', 'size':12}
matplotlib.rc('font',**font)

# Load percent sewered output from ahs_cbsa.py

percent_sewered_df = pd.read_csv('../outputs/ahs_sewer_connectivity_by_cbsa.csv', index_col = 0)

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
        'variable_type':'PERPOVLVL',
        'variable_type_description':'Poverty level',
        'variable_values':['0', '100'],
        'variable_descriptions':['In poverty', 'Not in poverty']
    },
    {
        'variable_type':'NUMPEOPLE',
        'variable_type_description':'Household size',
        'variable_values':['1', '2', '3', '4'],
        'variable_descriptions':['1', '2', '3', '4+']
    }
]

# Make plot

fig, ax = plt.subplots(6,1, figsize = (19,13), sharex = True, gridspec_kw = {'wspace':0})

percent_sewered_df_overall_sorted = percent_sewered_df[percent_sewered_df['variable_type']=='overall'].sort_values('percent_sewered', ascending = False)

# Get the order of the locations (in this case ordered from highest connectivity to lowest connectivity)
geo_values = percent_sewered_df_overall_sorted['geo_value'].values
geo_descriptions = percent_sewered_df_overall_sorted['geo_description'].values
x = np.array(range(len(geo_values)))
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:cyan', 'tab:red', 'tab:purple']

# Reformat the CBSA descriptions to make them easier to display
geo_description_plot =[]
for geo_description in geo_descriptions:
    geo_split = geo_description.split(', ')
    if len(geo_split)==2:
        cities = geo_split[0]
        states = geo_split[1]
        cities_split = cities.split('-')
        states_split = states.split('-')
        geo_description_plot.append(cities_split[0] + ', ' + states_split[0])
    else:
        geo_description_plot.append(geo_description)

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
                    yerr_lower = 0
                if yerr_upper<0:
                    yerr_upper = 0
                
                if ~np.isnan(dely):
                    max_abs_value = np.max(np.array([max_abs_value, np.abs(dely-yerr_lower), np.abs(dely+yerr_upper)]))
                
                p1 = ax[i].bar(k*8-round(len(variable_values)/2)+j*width, dely, yerr = [[yerr_lower], [yerr_upper]], width = width, color = color, error_kw = {'lw':0.5}, capsize = 0.5)
                ax[i].plot([k*8-4, k*8-4], [-50, 50], linestyle = ':', color = 'k', linewidth = 0.5, alpha = 0.5)
                
                j+=1
                if k==0:
                    # Only display legend once (not for every location)
                    p.append(p1)
        k+=1
    
    # Make the plot pretty
    if variable_type=='overall':
        ax[i].set_ylim([0, 100])
        ax[i].set_ylabel('% of households \nconnected to sewer')
    else:   
        ax[i].plot([x[0]-4, 8*x[-1]+4], [0, 0], 'k-', linewidth = 0.5)
        ax[i].set_ylim([-1.1*max_abs_value, 1.1*max_abs_value])
        ax[i].plot([k*8-4, k*8-4], [-1.1*max_abs_value, 1.1*max_abs_value], linestyle = ':', color = 'lightgrey', linewidth = 0.5)
        # ax[i].text(0, 0.8*max_abs_value, variable_type_description)
        ax[i].legend(p, variable_descriptions, loc = (1.01, 0), fontsize = 10)
    ax[i].set_title(variable_type_description)
    ax[i].set_xticks(x*8)
    ax[i].set_xticklabels(geo_description_plot, rotation = 90)
    ax[i].set_xlim([x[0]-4, x[-1]*8+4])
    
    i+=1
ax[3].set_ylabel('% of households connected to sewer - \n% of households connected to sewer in census division')
fig.suptitle('By core-based statistical areas (2019, 2021)')
plt.tight_layout()
plt.savefig('../figures/figsi_ahs_sewer_connectivity_by_cbsa.png', dpi = 300)
plt.savefig('../figures/figsi_ahs_sewer_connectivity_by_cbsa.pdf', dpi = 300)