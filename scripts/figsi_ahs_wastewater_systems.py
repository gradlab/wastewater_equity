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


# Make plot
ahsn = fnc.cleanup_column(ahsn, 'SEWTYPE', ahsdict)
fig = fnc.plot_cat_var(ahsn, labels, ahsdict, 'SEWTYPE', figsize = (9.5,4), plot_err = True)
fig.savefig('../figures/figsi_ahs_wastewater_systems.png')
fig.savefig('../figures/figsi_ahs_wastewater_systems.pdf')
