from zipfile import ZipFile
from urllib import request
import os
import shutil

# Download and unzip national 2021 file

if not os.path.exists('../data/ahs/puf_national_household_2021_v1.0.csv'):
    request.urlretrieve('https://www2.census.gov/programs-surveys/ahs/2021/AHS%202021%20National%20PUF%20v1.0%20CSV.zip', '../data/ahs/puf_national_2021_v1.0.zip')
    # Unzip metadata file
    if not os.path.exists('../data/ahs/puf_national_2021_v1.0/'):
        os.mkdir('../data/ahs/puf_national_2021_v1.0/')
        with ZipFile('../data/ahs/puf_national_2021_v1.0.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/ahs/puf_national_2021_v1.0/')

    # Copy and rename file        
    shutil.copyfile('../data/ahs/puf_national_2021_v1.0/household.csv', '../data/ahs/puf_national_household_2021_v1.0.csv')

    # Delete unused files
    shutil.rmtree('../data/ahs/puf_national_2021_v1.0/')
    os.remove('../data/ahs/puf_national_2021_v1.0.zip')
    
# Metropolitan 2021 file

if not os.path.exists('../data/ahs/puf_metropolitan_household_2021_v1.0.csv'):
    request.urlretrieve('https://www2.census.gov/programs-surveys/ahs/2021/AHS%202021%20Metropolitan%20PUF%20v1.0%20CSV.zip', '../data/ahs/puf_metropolitan_2021_v1.0.zip')
    # Unzip metadata file
    if not os.path.exists('../data/ahs/puf_metropolitan_2021_v1.0/'):
        os.mkdir('../data/ahs/puf_metropolitan_2021_v1.0/')
        with ZipFile('../data/ahs/puf_metropolitan_2021_v1.0.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/ahs/puf_metropolitan_2021_v1.0/')

    # Copy and rename file        
    shutil.copyfile('../data/ahs/puf_metropolitan_2021_v1.0/household.csv', '../data/ahs/puf_metropolitan_household_2021_v1.0.csv')

    # Delete unused files
    shutil.rmtree('../data/ahs/puf_metropolitan_2021_v1.0/')
    os.remove('../data/ahs/puf_metropolitan_2021_v1.0.zip')

# Metropolitan 2019 file

if not os.path.exists('../data/ahs/puf_metropolitan_household_2019_v1.0.csv'):
    request.urlretrieve('https://www2.census.gov/programs-surveys/ahs/2019/AHS%202019%20Metropolitan%20PUF%20v1.0%20CSV.zip', '../data/ahs/puf_metropolitan_2019_v1.0.zip')
    # Unzip metadata file
    if not os.path.exists('../data/ahs/puf_metropolitan_2019_v1.0/'):
        os.mkdir('../data/ahs/puf_metropolitan_2019_v1.0/')
        with ZipFile('../data/ahs/puf_metropolitan_2019_v1.0.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/ahs/puf_metropolitan_2019_v1.0/')

    # Copy and rename file        
    shutil.copyfile('../data/ahs/puf_metropolitan_2019_v1.0/household.csv', '../data/ahs/puf_metropolitan_household_2019_v1.0.csv')

    # Delete unused files
    shutil.rmtree('../data/ahs/puf_metropolitan_2019_v1.0/')
    os.remove('../data/ahs/puf_metropolitan_2019_v1.0.zip')
    
# National 2013 file

if not os.path.exists('../data/ahs/puf_national_household_2013_v2.0.csv'):
    request.urlretrieve('https://www2.census.gov/programs-surveys/ahs/2013/AHS%202013%20National%20PUF%20v2.0%20CSV.zip', '../data/ahs/puf_national_2013_v2.0.zip')
    # Unzip metadata file
    if not os.path.exists('../data/ahs/puf_national_2013_v2.0/'):
        os.mkdir('../data/ahs/puf_national_2013_v2.0/')
        with ZipFile('../data/ahs/puf_national_2013_v2.0.zip', 'r') as zip_ref:
            zip_ref.extractall('../data/ahs/puf_national_2013_v2.0/')

    # Copy and rename file        
    shutil.copyfile('../data/ahs/puf_national_2013_v2.0/household.csv', '../data/ahs/puf_national_household_2013_v2.0.csv')

    # Delete unused files
    shutil.rmtree('../data/ahs/puf_national_2013_v2.0/')
    os.remove('../data/ahs/puf_national_2013_v2.0.zip')
