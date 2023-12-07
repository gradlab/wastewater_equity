import pandas as pd
import numpy as np
from scipy.stats import binom
from scipy.integrate import cumtrapz

def cleanup_column(ahsn, col_name, ahsdict):
    """Cleaning up AHS data. Data is imported as strings of strings, and this gets rid of the extra set of quotation marks"""
    col = ahsn[col_name]
    col_clean = np.empty(len(col)).astype('str')
    if ahsdict[ahsdict['Variable']==col_name]['Type'].values[0] == 'Character':
        for i in range(len(col)):
            entry = col[i].replace("'", "")
            if entry == '-6':
                col_clean[i] = 'N'
            elif entry == '-9':
                col_clean[i] = 'M'
            else:
                col_clean[i] = str(entry)
    else:
        col = col.astype('str')
        for i in range(len(col)):
            entry = col[i]
            if entry == '-6':
                col_clean[i] = 'Not applicable'
            else:
                col_clean[i] = entry
    ahsn[col_name] = col_clean
    return ahsn

def get_labels(labels, col_name):
    """Gets the codebook for the variable values"""
    return labels[(labels['Table'] == 'HOUSEHOLD')&(labels['NAME']==col_name)]   

def calc_summary_stats_replicates(weighted_replicates, num_values, num_reps):
    """Calculates the mean, median, and 95% CIs"""
    weighted_rep_mean = np.mean(weighted_replicates, axis = 0)
    weighted_rep_median = np.median(weighted_replicates, axis = 0)
    
    weighted_rep_var = (4/num_reps)*np.sum((weighted_replicates-np.tile(np.reshape(weighted_rep_mean,(1,num_values)),(num_reps,1)))**2, axis = 0)
    weighted_rep_95ci = 1.96*np.sqrt(weighted_rep_var)
    
    weighted_rep_95ci_lower = np.quantile(weighted_replicates, 0.025, axis = 0)
    weighted_rep_95ci_upper = np.quantile(weighted_replicates, 0.975, axis = 0)
    
    return weighted_rep_mean, weighted_rep_var, weighted_rep_95ci, weighted_rep_95ci_lower, weighted_rep_95ci_upper

def get_weighted_counts(ahsn,var,values):
    """Calculates the weighted counts"""
    weighted_counts = []
    for value in values:
        df = ahsn[ahsn[var]==value]
        weighted_counts.append(df['WGT90GEO'].sum())
    return weighted_counts

def get_weighted_counts_err(ahsn, var, values):
    """Calculates the 95% CIs for the weighted counts"""
    num_reps = 160
    num_values = len(values)
    weighted_counts_replicates = np.empty((num_reps, num_values))
    for j in range(len(values)):
        value = values[j]
        df = ahsn[ahsn[var]==value]
        for i in range(1,num_reps+1):
            weighted_counts_replicates[i-1, j] = df['REPWGT'+str(i)].sum()

    weighted_counts_rep_mean, weighted_counts_rep_var, weighted_counts_rep_95ci, weighted_counts_rep_95ci_lower, weighted_counts_rep_95ci_upper = calc_summary_stats_replicates(weighted_counts_replicates, num_values, num_reps)
    return weighted_counts_rep_mean, weighted_counts_rep_var, weighted_counts_rep_95ci, weighted_counts_rep_95ci_lower, weighted_counts_rep_95ci_upper

def get_weighted_percent(df, var, values):
    """Calculated the weighted percentages"""
    weighted_percent = []
    for value in values:
        df2 = df[df[var]==value]
        weighted_percent.append(100*df2['WGT90GEO'].sum()/df['WGT90GEO'].sum())
    return weighted_percent

def bayesian_binomial_ci(x, n):
    """Bayesian binomial inference for calculating errors in percentages when the point estimate is 0% or 100%"""
    p = np.linspace(0, 1, 10**5)
    unnorm = binom.pmf(x, n, p)
    denom = np.trapz(p, unnorm)
    norm = unnorm/denom
    cum_int = cumtrapz(p, norm, initial = 0)
    lower = 100*p[cum_int<=0.025][-1]
    upper = 100*p[cum_int>=0.975][0]
    return lower, upper 

def get_weighted_percent_err(df, var, values):
    """Calculates the 95% CIs for the weighted percentages"""
    num_reps = 160
    num_values = len(values)
    weighted_percent_replicates = np.empty((num_reps, num_values))

    for j in range(len(values)):
        value = values[j]
        df2 = df[df[var] == value]
        for i in range(1,num_reps+1):
            weighted_percent_replicates[i-1, j] = 100*df2['REPWGT'+str(i)].sum()/df['REPWGT'+str(i)].sum()
            
    weighted_percent_rep_mean, weighted_percent_rep_var, weighted_percent_rep_95ci, weighted_percent_rep_95ci_lower, weighted_percent_rep_95ci_upper = calc_summary_stats_replicates(weighted_percent_replicates, num_values, num_reps)
    if (weighted_percent_rep_mean == 0)|(weighted_percent_rep_mean == 100):
        weighted_percent_rep_95ci_lower = []
        weighted_percent_rep_95ci_upper = []
        for j in range(len(values)):
            value = values[j]
            df2 = df[df[var] == value]
            x = len(df2)
            n = len(df)
            lower, upper = bayesian_binomial_ci(x, n)
            weighted_percent_rep_95ci_lower.append(lower)
            weighted_percent_rep_95ci_upper.append(upper)
    return weighted_percent_rep_mean, weighted_percent_rep_var, weighted_percent_rep_95ci, weighted_percent_rep_95ci_lower, weighted_percent_rep_95ci_upper

def plot_cat_var(ahsn, labels, ahsdict, cat_var, figsize = (4,8), plot_err = True):
    """Plots a summary histogram for weighted counts of categorical variables"""
    fig = plt.figure(figsize = figsize)
    
    values = get_labels(labels, cat_var)['Value'].values
    weighted_counts = get_weighted_counts(ahsn, cat_var, values)
    
    x = np.array(range(len(values)))
    
    if plot_err: 
        weighted_counts_rep_mean, weighted_counts_rep_var, weighted_counts_rep_95ci, weighted_counts_rep_95ci_lower, weighted_counts_rep_95ci_upper = get_weighted_counts_err(ahsn, cat_var, values)
        p = plt.barh(x, weighted_counts, xerr = [[weighted_counts-weighted_counts_rep_95ci_lower, weighted_counts_upper-weighted_counts]])
    else:
        p = plt.barh(x, weighted_counts)

    plt.yticks(ticks = x, labels = get_labels(labels, cat_var)['Label'].values)

    plt.gca().invert_yaxis()
    plt.xscale('log')
    plt.ylabel('')
    plt.xlabel('Weighted number of households')
    plt.title(ahsdict[ahsdict['Variable'] == cat_var]['Description'].values[0])
    plt.tight_layout()
    plt.show()
    return fig

def get_percent_sewered(ahs, geo_type, ahsdict, labels, variable_type, variable_type_description, variable_values, variable_descriptions, min_households = 5): 
    """Getting the percent of a given population that is sewered"""
    
    ahs = cleanup_column(ahs, geo_type, ahsdict)
    geo_labels = get_labels(labels, geo_type)
    variable_class = get_labels(labels, variable_type)['Type'].values[0]
    
    percent_sewered = {'geo_value':[], 
                       'geo_description':[], 
                       'variable_type':[],
                       'variable_type_description':[],
                       'variable_value':[],
                       'variable_description':[],
                       'percent_sewered':[], 
                       'percent_sewered_lower':[], 
                       'percent_sewered_upper':[],
                      'num_observations':[]}

    # Check if the variable is categorical
    if variable_class == 'C':
        # Loop through all values of the geographical variable
        for value, df in ahs.groupby(geo_type):
            # Loop through all values of the demograhpical/economic variable
            for i in range(len(variable_values)):
                percent_sewered['geo_value'].append(value)
                percent_sewered['geo_description'].append(geo_labels[geo_labels['Value'].values==value]['Label'].values[0])

                variable_value = variable_values[i]
                variable_description = variable_descriptions[i]
                percent_sewered['variable_type'].append(variable_type)
                percent_sewered['variable_type_description'].append(variable_type_description)
                percent_sewered['variable_value'].append(variable_value)
                percent_sewered['variable_description'].append(variable_description)
                
                df2 = df[df[variable_type]==variable_value]
                
                # Check that there is more than the minimum number of households in this group
                if len(df2)>=min_households:
                    percent_sewered['percent_sewered'].append(get_weighted_percent(df2, 'SEWTYPE_summary', ['Public sewer'])[0])
                    _, _, _, weighted_percent_rep_95ci_lower, weighted_percent_rep_95ci_upper = get_weighted_percent_err(df2, 'SEWTYPE_summary', ['Public sewer'])
                    percent_sewered['percent_sewered_lower'].append(weighted_percent_rep_95ci_lower[0])
                    percent_sewered['percent_sewered_upper'].append(weighted_percent_rep_95ci_upper[0])
                    percent_sewered['num_observations'].append(len(df2))
                else:
                    percent_sewered['percent_sewered'].append(np.nan)
                    percent_sewered['percent_sewered_lower'].append(np.nan)
                    percent_sewered['percent_sewered_upper'].append(np.nan)
                    percent_sewered['num_observations'].append(len(df2))
              
    # Check if the variable is numerical
    elif variable_class == 'N':
        # Remove households that had "not applicable" entry for this variable
        ahs_numerical = ahs[ahs[variable_type]!='Not applicable']
        ahs_numerical[variable_type] = ahs_numerical[variable_type].astype('float')
        
        # Loop through all values of the geographical variable
        for value, df in ahs_numerical.groupby(geo_type):
            
            # Loop through all value ranges of the demograhpic/economic variable
            for i in range(len(variable_values)):
                percent_sewered['geo_value'].append(value)
                percent_sewered['geo_description'].append(geo_labels[geo_labels['Value'].values==value]['Label'].values[0])
                
                # Get the lower and upper bounds on the range of values for this group
                variable_value_lower = variable_values[i]
                if i<len(variable_values)-1:
                    variable_value_upper = variable_values[i+1]
                else:
                    variable_value_upper = np.inf
                variable_description = variable_descriptions[i]

                percent_sewered['variable_type'].append(variable_type)
                percent_sewered['variable_type_description'].append(variable_type_description)
                percent_sewered['variable_value'].append(variable_value_lower)
                percent_sewered['variable_description'].append(variable_description)
                
                df2 = df[(df[variable_type]>=variable_value_lower)&(df[variable_type]<variable_value_upper)]
                
                # Check that there is more than the minimum number of households
                if len(df2)>=min_households:
                    percent_sewered['percent_sewered'].append(get_weighted_percent(df2, 'SEWTYPE_summary', ['Public sewer'])[0])
                    _, _, _, weighted_percent_rep_95ci_lower, weighted_percent_rep_95ci_upper = get_weighted_percent_err(df2, 'SEWTYPE_summary', ['Public sewer'])
                    percent_sewered['percent_sewered_lower'].append(weighted_percent_rep_95ci_lower[0])
                    percent_sewered['percent_sewered_upper'].append(weighted_percent_rep_95ci_upper[0])
                    percent_sewered['num_observations'].append(len(df2))
                else:
                    percent_sewered['percent_sewered'].append(np.nan)
                    percent_sewered['percent_sewered_lower'].append(np.nan)
                    percent_sewered['percent_sewered_upper'].append(np.nan)
                    percent_sewered['num_observations'].append(len(df2))
    else:
        raise ValueError('Variable class is neither categorical (C) nor numerical (N): ' + variable_class)
        
    percent_sewered_df = pd.DataFrame(percent_sewered)
    percent_sewered_df['geo_type'] = geo_type
    return percent_sewered_df

def get_percent_sewered_overall(ahs, geo_type, labels, min_households = 5): 
    """Get the overall percentage of a geographical subdivision that is sewered"""
    
    geo_labels = get_labels(labels, geo_type)
    
    percent_sewered = {}
    percent_sewered.update({'geo_type':[], 
                               'geo_value':[], 
                               'geo_description':[], 
                               'variable_type':[],
                               'variable_type_description':[],
                               'variable_value':[],
                               'variable_description':[],
                               'percent_sewered':[], 
                               'percent_sewered_lower':[], 
                               'percent_sewered_upper':[],
                           'num_observations':[]})

    variable_type = 'overall'
    variable_type_description = 'Overall'
    variable_value = 'overall'
    variable_description = 'overall'

    for value, df in ahs.groupby(geo_type):
        percent_sewered['geo_type'].append(geo_type)
        percent_sewered['geo_value'].append(value)
        percent_sewered['geo_description'].append(geo_labels[geo_labels['Value'].values==value]['Label'].values[0])
        percent_sewered['variable_type'].append('overall')
        percent_sewered['variable_type_description'].append(variable_type_description)
        percent_sewered['variable_value'].append('overall')
        percent_sewered['variable_description'].append('overall')
        percent_sewered['percent_sewered'].append(get_weighted_percent(df, 'SEWTYPE_summary', ['Public sewer'])[0])
        _, _, _, weighted_percent_rep_95ci_lower, weighted_percent_rep_95ci_upper = get_weighted_percent_err(df, 'SEWTYPE_summary', ['Public sewer'])
        percent_sewered['percent_sewered_lower'].append(weighted_percent_rep_95ci_lower[0])
        percent_sewered['percent_sewered_upper'].append(weighted_percent_rep_95ci_upper[0])
        percent_sewered['num_observations'].append(len(df))
    return pd.DataFrame(percent_sewered)