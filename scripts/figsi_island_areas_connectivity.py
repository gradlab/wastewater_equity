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

def get_df_for_plotting(merged):
    df_wide = gpd.GeoDataFrame()

    df = merged[['place_name', 'place_fips', 'frac_sewer', 'geometry']]
    df.rename({'frac_sewer':'frac_households'}, axis = 'columns', inplace = True)
    df['sewage_type'] = 'Sewer'
    df_wide = df_wide.append(df)

    df = merged[['place_name', 'place_fips', 'frac_septic', 'geometry']]
    df.rename({'frac_septic':'frac_households'}, axis = 'columns', inplace = True)
    df['sewage_type'] = 'Septic'
    df_wide = df_wide.append(df)

    df = merged[['place_name', 'place_fips', 'frac_other', 'geometry']]
    df.rename({'frac_other':'frac_households'}, axis = 'columns', inplace = True)
    df['sewage_type'] = 'Other'
    df_wide = pd.concat([df_wide, df])

    df_wide['frac_households'] = 100*df_wide['frac_households']
    df_wide.reset_index(drop = True, inplace = True)
    return df_wide

def make_plot(df_wide, output_filename_no_suffix, title):
    plt.figure(figsize = (4,3.5))

    sns.stripplot(data = df_wide, x = 'sewage_type', y = 'frac_households', color = 'gray', edgecolor = 'k', linewidth = 0.5, alpha = 0.5)
    sns.boxplot(data = df_wide, x = 'sewage_type', y = 'frac_households')
    plt.xlabel('Sewage type')
    plt.ylabel('Percentage of households')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_filename_no_suffix + '.png')
    plt.savefig(output_filename_no_suffix + '.pdf')
    
def make_map(df_wide, output_filename_no_suffix, title):
    plt.figure(figsize = (10,3))
    i = 1
    sewage_types = ['Sewer', 'Septic', 'Other']
    for sewage_type in sewage_types:
        df_subset = df_wide[df_wide['sewage_type']==sewage_type]
        ax = plt.subplot(1,3,i)
        ax.axis('off')
        if i == 3:
            df_subset.plot(ax = ax, column = 'frac_households', categorical = False, legend = True, vmin = 0, vmax = 100, legend_kwds={'label':'Percentage of households'})
        else:
            df_subset.plot(ax = ax, column = 'frac_households', categorical = False, legend = False, vmin = 0, vmax = 100)
        plt.xticks([])
        plt.yticks([])
        plt.title(sewage_type + ', ' + title)
        i+=1
    plt.tight_layout()
    plt.savefig(output_filename_no_suffix + '_map.png')
    plt.savefig(output_filename_no_suffix + '_map.pdf')

def merge_shapefile(df, shapes_filename):
    shapes = gpd.read_file(shapes_filename)
    shapes = shapes[['PLACEFP', 'geometry']]
    shapes.rename({'PLACEFP':'place_fips'}, axis = 'columns', inplace = True)
    shapes['place_fips'] = shapes['place_fips'].astype('int')

    merged = shapes.merge(df, on = ['place_fips'], how = 'outer')
    return merged
    
def run_main(data_filename, shapes_filename, output_filename_no_suffix, title):
    df = pd.read_csv(data_filename, index_col = 0)
    merged = merge_shapefile(df, shapes_filename)
    df_wide = get_df_for_plotting(merged)
    make_plot(df_wide, output_filename_no_suffix, title)
    make_map(df_wide, output_filename_no_suffix, title)
    
# American Samoa

data_filename = '../outputs/island_areas_sewer_connectivity_american_samoa.csv'
shapes_filename = '../data/geography_files/tl_2020_60_place/tl_2020_60_place.shp'
output_filename_no_suffix = '../figures/figsi_island_areas_connectivity_american_samoa'
title = 'American Samoa'

run_main(data_filename, shapes_filename, output_filename_no_suffix, title)

# Guam

data_filename = '../outputs/island_areas_sewer_connectivity_guam.csv'
shapes_filename = '../data/geography_files/tl_2020_66_place/tl_2020_66_place.shp'
output_filename_no_suffix = '../figures/figsi_island_areas_connectivity_guam'
title = 'Guam'

run_main(data_filename, shapes_filename, output_filename_no_suffix, title)

# Northern Mariana Islands

data_filename = '../outputs/island_areas_sewer_connectivity_northern_mariana_islands.csv'
shapes_filename = '../data/geography_files/tl_2020_69_place/tl_2020_69_place.shp'
output_filename_no_suffix = '../figures/figsi_island_areas_connectivity_northern_mariana_islands'
title = 'Northern Mariana Islands'

run_main(data_filename, shapes_filename, output_filename_no_suffix, title)

# Virgin Islands

data_filename = '../outputs/island_areas_sewer_connectivity_virgin_islands.csv'
shapes_filename = '../data/geography_files/tl_2020_78_place/tl_2020_78_place.shp'
output_filename_no_suffix = '../figures/figsi_island_areas_connectivity_virgin_islands'
title = 'Virgin Islands'

run_main(data_filename, shapes_filename, output_filename_no_suffix, title)
