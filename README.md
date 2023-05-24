# wastewater_equity
Data and code for "Assessment of sewer connectivity in the United States and its implications for equity in wastewater-based epidemiology"

## scripts/
* `ahs*.py`: scripts and functions for the analysis of the American Housing Survey data. `ahs_download_data.py` should be run first, then the other scripts.
* `epa*.py`: scripts for the analysis of the Environmental Protection Agency Clean Watersheds Needs Survey data. `epa_preprocessing.py` should be run first, then `epa_analysis.py`.
* `fig*.py`: scripts for reproducing the figures in the manuscript. Note that figure scripts use the outputs of the other analysis scripts (saved to `outputs/`) 
* `florida*.py`: scripts for the analysis of the Florida Department of Health septic tank inspection permits data. `florida_septic_preprocessing.py` should be run first, then `florida_septic_analysis.py`.
* `island_areas*.py`: scripts for the analysis of the island areas. 
* `mathematical_modeling_functions.py`: functions for the mathematical model of two interacting populations
* `table*.py`: scripts for reproducing the tables in the manuscript
* `utah*.py`: script for the analysis of the population connected to sewers in Utah

## data/
### acs/
Data files from the [American Community Survey](https://www.census.gov/programs-surveys/acs), downloaded from the [US Census Data website](https://data.census.gov/)
### ahs/
Dictionaries and references from the [American Housing Survey](https://www.census.gov/programs-surveys/ahs.html) (AHS). Note that the data files from the AHS are too large to be put on Github (>100MB) and are downloaded directly from the [AHS website](https://www.census.gov/programs-surveys/ahs/data.html) in `ahs_download_data.py` and deposited into this folder.
### epa/
Data files from the Environmental Protection Agency [Clean Watersheds Needs Survey](https://www.epa.gov/sites/default/files/2015-10/documents/cwns_2012_detailed_scope_and_methods-508.pdf), downloaded from the [EPA Data Downloads website](https://ordspub.epa.gov/ords/cwns2012/f?p=cwns2012:25) and extracted from a Microsoft Access database file to csv files using the [mdbtools](https://github.com/mdbtools/mdbtools) package.
### florida_septic_inspections/
Data files from the Florida Department of Health septic tank inspection permits database, downloaded from the [Florida Geographic Data Library](https://fgdl.org/zips/metadata/xml/septic_jun12.xml).
### geography_files/
Shapefiles and geography conversion files from the US Census used for mapping.
### islands/
Data files from the [US Census Island Areas Decennial Survey](https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/release/2020-island-areas-data-products.html), downloaded from the [US Census Data website](https://data.census.gov/)
### minnesota/
Data files from the [Minnesota Wastewater Infrastructure Needs Survey](https://www.pca.state.mn.us/sites/default/files/wq-wwtp3-06.pdf), provided by the Minnesota Pollution Control Agency. Data files from the Minnesota Subsurface Sewage Treatment Systems Survey, taken from the [2017 SSTS Annual Report on Subsurface Sewage Treatment Systems in Minnesota](https://www.pca.state.mn.us/sites/default/files/wq-wwists1-58.pdf).
### utah/
Data from the [Utah Municipal Wastewater Planning Survey](https://deq.utah.gov/water-quality/municipal-wastewater-planning-program-mwpp) was provided by the Utah Department of Environment Quality, Division of Water Quality and was not included in this repository. The latest version of the data can be requested from hcampbell[at]utah[dot]gov.

## outputs/
Outputs from the scripts, including tables in the manuscript

## figures/
Figures in the manuscript
