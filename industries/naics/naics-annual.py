# %% [markdown]
# # County NAICS Files
# After running the notebook, delete the data_raw folder<br>
# Zip level not available -> https://api.census.gov/data/2011/cbp/variables.html<br>
# This notebook is a filtered and edited version of us_econ_old.ipynb for generating yearly data.<br>
# For earlier code that generates averaged data aver years please refer us_econ_old.ipynb.<br>
# This notebook will start generating data from year 2017.
# Output resides in the community-data repository in industries/{<i>variable</i>}-update folders within indistries.<br>
# We copy manually to community-data/indutries/{<i>variable</i>} folders.

# %%
import csv
import requests as r
import pandas as pd
import zipfile, io
import os
from tqdm import tqdm
import pathlib
import datetime
import requests as r
from pathlib import Path
import os
import pickle
import time

endyear = datetime.date.today().year
api_headers = {}
api_headers['x-api-key'] = '975f39a54e48438ceebf303d6018e34db212e804'

# %%
# Set a relative location to save the data from the request
repo_dir = pathlib.Path().cwd()
#print(repo_dir)

raw_data_dir = repo_dir / 'data_raw'
out_data_dir = raw_data_dir / 'BEA_Industry_Factors'
    
county_data_dir = out_data_dir / 'county_level'
if not county_data_dir.exists():
    county_data_dir.mkdir(parents=True)


# %%
# Load the state FIPS codes key
state_fips = pd.read_csv('../../../community-data/us/id_lists/state_fips.csv', usecols=['Name', 'Postal Code', 'FIPS'])
state_fips = state_fips.head(50)  # <-- limit to only US states, not teritories

# %%
# Base URL for the API call
base_url = "https://api.census.gov/data"

#
# NOTE Years Prior to 2012 Currently have a bug when specifying NAICS#### as one of the columns
#      - stick to 2012 and later for now
#

def get_county_cbp(fips, state, years):
    count = 0
    for year in years:
        print(f"Getting data for state: {state}\tyear: {year}")
        if year >= 2000 and year <= 2002:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS1997_TTL,ESTAB,EMP,PAYANN"
            url = f"{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}"
        elif year >= 2003 and year <=2007:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2002_TTL,ESTAB,EMP,PAYANN"
            url = f"{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}"
        elif year >= 2008 and year <= 2011:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2007_TTL,ESTAB,EMP,PAYANN"
            url = f"{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}"
        elif year >= 2012 and year <= 2016:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2012,NAICS2012_TTL,ESTAB,EMP,PAYANN"
            url = f"{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}"
        elif year >= 2017 and year <= 2021:
            columns_to_select = "GEO_ID,NAME,COUNTY,YEAR,NAICS2017,NAICS2017_LABEL,ESTAB,EMP,PAYANN"
            url = f"{base_url}/{year}/cbp?get={columns_to_select}&for=county:*&in=state:{fips:02d}"
    
    
        response = r.get(url, headers=api_headers)

        with open(county_data_dir / f"industriesPerCounty_{str.lower(state.replace(' ', ''))}_{year}.csv",'w') as resultPath:
            for line in response.text.strip().split('\n'):
                line=line.replace('[',"").replace(']',"")
                resultPath.write(line + "\n")

        print("  > Finished CSV for year"+str(year))

# %%
#Years Initialization for data generation
startyear = 2017
endyear = 2021

# %%
for fips in state_fips.FIPS.unique():
     state = state_fips.query(f'FIPS=={fips}').values[0][0]
     years=range(startyear, endyear+1)
     get_county_cbp(fips, state, years)

# %% [markdown]
# # Data Aggregation
# This part allows us to manage different Fips level (county/state) and different NAICS level (sector/industry/etc...)  
# Trick: Getting the NAICS code from all the NAICS files that we downloaded

# %%
# Load the data from startyear

def load_all_states(bea_data_dir):
    
    for i in range(startyear,endyear+1):

        x="_"+str(i)
        files = [f for f in bea_data_dir.iterdir() if x in f.name]

        for f in files:

            # variable selection based on census year
            naics_str = "NAICS2012" if i < 2017 else "NAICS2017"
            naics_ttl = "NAICS2012_TTL" if i < 2017 else "NAICS2017_LABEL"
            geo_ttl = "GEO_TTL" if i < 2017 else "NAME"

            df = pd.read_csv(f,encoding='latin-1',dtype={naics_str: str})
            if 'Unnamed: 11' in df.columns:
                df=df.drop("Unnamed: 11", axis=1)
            if 'Unnamed: 10' in df.columns:
                df=df.drop("Unnamed: 10", axis=1)

            # renaming columns so similar data from 2012 census & 2017 census are entered into appropriate columns
            df = df.rename(columns={"fips": "id", naics_str: "relevant_naics","EMP":"emp","PAYANN":"payann","ESTAB":"estab", naics_ttl:"NAICS_TTL", geo_ttl:"GEO_TTL"})
            naics_str = "relevant_naics"
            naics_ttl = "NAICS_TTL"
            geo_ttl = "GEO_TTL"

            df['is5'] = df[naics_str].apply(lambda x: 'True' if len(x) == 5 else 'False')

            df.loc[(df['is5'] == 'True') & (df[naics_str].apply(lambda v: v[2:3]) == '-'), 'NAICS_Sector'] = df[naics_str]
            df.loc[(df['is5'] == 'True') & (df[naics_str].apply(lambda v: v[2:3]) != '-'), 'NAICS_Sector'] = df[naics_str].apply(lambda v: v[:2])
            df.loc[(df['is5'] == 'False') , 'NAICS_Sector'] = df[naics_str].apply(lambda v: v[:2])

            yield df
    
df = pd.concat(load_all_states(county_data_dir)).drop("is5", axis=1)

#df

# %%
df=df.drop("county", axis=1)

# %% [markdown]
# ### Process FIPS Code
# FIPS is the federal/census unique ID for each geographic area.  States have 2 digives and counties have 5

# %%
# Process FIPS code
df['fips'] = df.GEO_ID.apply(lambda GID: GID.split('US')[1])

def county_level(df):
    return df[df['id'].str.len() == 5]

def state_level(df):
    return df[df['id'].str.len() == 2]

# %%
# NOTE If this block is run please delete the generated file before pushing into repo (file size too large)
#df.to_csv("allll.csv")

# %% [markdown]
# ### Renaming Columns for aggregate df
# Note that we are no longer averaging data for all years. That remains in the original us_econ_old notebook

# %%
newDF = df.rename(columns={"fips": "id","EMP":"emp","PAYANN":"payann","ESTAB":"estab"})
newDF

# %%
newDF.tail(50)

# %% [markdown]
# ### Group data by NAICS Sector
# 
# NAICS is the North American Industry Classification System. The coarsest level of classification is the *Sector*.
# 
# The organization of NAICS is as follows:  <-- from [this page](https://www.census.gov/programs-surveys/economic-census/guidance/understanding-naics.html) on census.gov
# - Sector: 2-digit code
#     - Subsector: 3-digit code
#         - Industry Group: 4-digit code
#             - NAICS Industry: 5-digit code
#                 - National Industry: 6-digit code
# 
# Start by grouping the data by sector:

# %%
def naics_level(df, naics_level):
    return df[df['relevant_naics'].str.len() == naics_level]

# %%
df_naics_2 = naics_level(newDF, 2).reset_index(drop=True)
df_naics_3 = naics_level(newDF, 3).reset_index(drop=True)
df_naics_4 = naics_level(newDF, 4).reset_index(drop=True)
df_naics_5 = naics_level(newDF, 5).reset_index(drop=True)
df_naics_6 = naics_level(newDF, 6).reset_index(drop=True)

df_naics_2 = df_naics_2[df_naics_2.relevant_naics != '00']
df_naics_3 = df_naics_3[df_naics_3.relevant_naics != '00']
df_naics_4 = df_naics_4[df_naics_4.relevant_naics != '00']
df_naics_5 = df_naics_5[df_naics_5.relevant_naics != '00']
df_naics_6 = df_naics_6[df_naics_6.relevant_naics != '00']

# %%
#s2=state_level(df_naics_2)
c2=county_level(df_naics_2)
#s3=state_level(df_naics_3)
#c3=county_level(df_naics_3)
#s4=state_level(df_naics_4)
c4=county_level(df_naics_4)
#s5=state_level(df_naics_5)
#c5=county_level(df_naics_5)
s6=state_level(df_naics_6)
#c6=county_level(df_naics_6)

# %%
newDF

# %% [markdown]
# Skipped the code block for `The statewide data does not include NAICS starting with 1!` from us_econ nb

# %% [markdown]
# # NAICS code to name translation
# Using 2012 naics codes and industries since 2017 naics codes & industries are not available in the current crosswalks data.<br>
# TODO: Update the 2012 codes with 2017 codes for updated data

# %%
NAICS_codes = pd.read_csv('../../../community-data/us/Crosswalk_MasterCrosswalk.csv', usecols=['2012_NAICS_Code', '2012_NAICS_Industry'])

# %%
NAICS_codes=NAICS_codes.rename(columns={"2012_NAICS_Code": "relevant_naics", "2012_NAICS_Industry": "industry_detail"})

# %%
NAICS_codes=NAICS_codes.dropna()

# %%
NAICS_codes=NAICS_codes.drop_duplicates()

# %%
NAICS_codes

# %%
#adding the row for Industries not classified
NAICS_codes
new_row = {'relevant_naics':99, 'industry_detail':"Industries not classified"}

#append row to the dataframe
NAICS_codes = pd.concat([NAICS_codes, pd.DataFrame([new_row])], ignore_index=True)

# %%
NAICS_codes

# %%
NAICS_codes.to_csv('../../../community-data/us/id_lists/industry_ID_list.csv')

# %% [markdown]
# # Making a states json

# %%
stateFips = pd.read_csv('../../../community-data/us/id_lists/state_fips.csv')

# %%
stateFips=stateFips.drop(['Unnamed: 3','Unnamed: 4','Unnamed: 5','Unnamed: 6'],axis=1)

# %%
stateFips

# %%
#stateFips.to_json(county_data_dir/'states.json', orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

# %% [markdown]
# # Making county to fips csv

# %%
countyDF=c2[['GEO_TTL','id']].drop_duplicates()

# %%
countyDF

# %%
countyDF['hascomma'] = countyDF['GEO_TTL'].apply(lambda x: 'True' if ',' in x else 'False')
countyDF

# %%
countyDF.loc[(countyDF['hascomma'] == 'True'), 'county'] = countyDF.GEO_TTL.apply(lambda GTT: GTT.split(', ')[0])
countyDF.loc[(countyDF['hascomma'] == 'True'), 'state'] = countyDF.GEO_TTL.apply(lambda GTT: GTT.split(', ')[-1])

# %%
countyDF=countyDF[['state','county','id']].drop_duplicates()

# %%
countyDF = countyDF.dropna()

# %%
countyDF

# %%
stats = stateFips.rename(columns={"Name": "state"})

# %%
stats = stats.drop("FIPS",axis=1)
stats

# %%
countyDF = countyDF.merge(stats, on='state', how='left')

# %%
countyDF = countyDF.rename(columns={"Postal Code": "abvr"})
countyDF

# %% [markdown]
# # Saving the County level data

# %%
#NOTE Code block to generate individual county level files for each county. (Commented because no need of each county files)
# states = newDF.state.unique()
# #states=[13]

# df_naics_6 = df_naics_6.astype({'relevant_naics': 'string'})

# a = county_level(df_naics_2)
# b = county_level(df_naics_4)
# c = county_level(df_naics_6)

# for state in states:
#     stateName = stateFips.loc[stateFips.FIPS==state,"Postal Code"].values[0]
#     print(stateName)

#     repo_dir = pathlib.Path().cwd()
#     state_dir = repo_dir.parents[2] / 'community-data' / 'industries' / 'naics' / 'US' / 'counties-update' / stateName
    
#     if not state_dir.exists():
#         state_dir.mkdir(parents=True)
    
#     a1 = a[a.state==state]
#     b1 = b[b.state==state]
#     c1 = c[c.state==state]

#     for year in range(startyear, endyear+1):
#         print(year)

#         a1y = a1[a1.YEAR==year]
#         b1y = b1[b1.YEAR==year]
#         c1y = c1[c1.YEAR==year]

#         def save_county_data(state, df, counties, naics_level_str):
#             for county in counties:

#                 curr_df = df[df.COUNTY==county]
                
#                 county = str(county)
#                 # print(county)
#                 if len(county) == 2:
#                     county = "0" + county
#                 elif len(county) == 1:
#                     county = "00" + county

#                 state = str(state) if len(str(state)) == 2 else "0" + str(state)

#                 curr_df = curr_df.drop(["GEO_ID", "GEO_TTL", "COUNTY", "YEAR", "NAICS_TTL", "state", "NAICS_Sector"], axis=1)
#                 curr_df = curr_df.rename(columns={"id":"fips"})

#                 filename = "US" + state + county + "-" + "census-" + naics_level_str + "-" + str(year) + ".csv"
                  
                 #NOTE: Need to change output path if the nb is transferred to data-pipeline repository
#                 curr_df.to_csv(f"../../../industries/naics/US/counties-update/state-naics-update/{stateName}/{filename}")

#         c_a1 = a1.COUNTY.unique()
#         c_b1 = b1.COUNTY.unique()
#         c_c1 = c1.COUNTY.unique()

#         save_county_data(state, a1y, c_a1, "naics2")
#         save_county_data(state, b1y, c_b1, "naics4")
#         save_county_data(state, c1y, c_c1, "naics6")

# %%
states = newDF.state.unique()
#states=[13]

df_naics_6 = df_naics_6.astype({'relevant_naics': 'string'})

a = county_level(df_naics_2)
b = county_level(df_naics_4)
c = county_level(df_naics_6)

for state in states:
    stateName = stateFips.loc[stateFips.FIPS==state,"Postal Code"].values[0]
    print(stateName)

    repo_dir = pathlib.Path().cwd()
    # state_dir = repo_dir.parents[2] / 'us' / 'state-naics-update' / stateName
    state_dir = repo_dir.parents[2] / 'community-data' / 'industries' / 'naics' / 'US' / 'counties-update' / stateName

    
    if not state_dir.exists():
        state_dir.mkdir(parents=True)
    
    a1 = a[a.state==state]
    b1 = b[b.state==state]
    c1 = c[c.state==state]

    for year in range(startyear, endyear+1):
        print(year)

        a1y = a1[a1.YEAR==year]
        b1y = b1[b1.YEAR==year]
        c1y = c1[c1.YEAR==year]

        def save_county_data(state, df, naics_level_str):

            state = str(state) if len(str(state)) == 2 else "0" + str(state)

            curr_df = df.drop(["GEO_ID", "GEO_TTL", "COUNTY", "YEAR", "NAICS_TTL", "state", "NAICS_Sector"], axis=1)
            curr_df = curr_df.rename(columns={"id":"Fips", "relevant_naics":"Naics", "estab":"Establishments", "emp":"Employees", "payann":"Payroll"})
            curr_df = curr_df[["Fips", "Naics", "Establishments", "Employees", "Payroll"]]

            filename = "US-" + stateName + "-" + "census-" + naics_level_str + "-counties-" + str(year) + ".csv"

            curr_df.to_csv(f"../../../community-data/industries/naics/US/counties-update/{stateName}/{filename}", index=False)
        
        save_county_data(state, a1y, "naics2")
        save_county_data(state, b1y, "naics4")
        save_county_data(state, c1y, "naics6")

# %% [markdown]
# # saving the statewide data
# Comment & uncomment the following code block with caution

# %%
#NOTE: Activate this cell only if you want to generate state naics data USING county cbp api (NOT the state cbp api)
#NOTE: If this block is activated, comment the data generation block for state naics which is using state cbp api request directly

# states=newDF.state.unique()
# #states=[13]

# for state in states:
    
#     b1 = county_level(df_naics_2)
#     c1 = b1[b1.state==state]
#     c1.astype({'NAICS_Sector': 'int'})
#     d1 = c1.groupby(['NAICS_Sector','NAICS_TTL','state','relevant_naics', "YEAR"],as_index=False).sum()
#     d1 = d1.drop(["COUNTY","id", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state", "GEO_ID"],axis=1)
#     # d1.insert(0, 'Fips', state)
#     # d1.insert(1, 'COUNTY', 999)
#     # d1.insert(2, 'GEO_TTL', 'Statewide')

#     b2 = county_level(df_naics_4)
#     c2 = b2[b2.state==state]
#     c2.astype({'NAICS_Sector': 'int'})
#     d2 = c2.groupby(['NAICS_Sector','NAICS_TTL','state','relevant_naics', "YEAR"],as_index=False).sum()
#     d2 = d2.drop(["COUNTY","id", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state", "GEO_ID"],axis=1)
#     # d2.insert(0, 'Fips', state)
#     # d2.insert(1, 'COUNTY', 999)
#     # d2.insert(2, 'GEO_TTL', 'Statewide')

#     b3 = county_level(df_naics_6)
#     c3 = b3[b3.state==state]
#     c3.astype({'NAICS_Sector': 'int'})
#     d3 = c3.groupby(['NAICS_Sector','NAICS_TTL','state','relevant_naics', "YEAR"],as_index=False).sum()
#     d3 = d3.drop(["COUNTY","id", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state", "GEO_ID"],axis=1)
#     # d3.insert(0, 'Fips', state)
#     # d3.insert(1, 'COUNTY', 999)
#     # d3.insert(2, 'GEO_TTL', 'Statewide')
    
#     stateName=stateFips.loc[stateFips.FIPS==state,"Postal Code"].values[0]
#     print(stateName)

    # repo_dir = pathlib.Path().cwd()
    # state_dir = repo_dir.parents[2] / 'community-data' / 'industries' / 'naics' / 'US' / 'states-update' / stateName
    
    # if not state_dir.exists():
    #     state_dir.mkdir(parents=True)

#     for year in range(startyear, endyear+1):
#         print(year)

#         def save_state_data(state, df, naics_level_str):
                
#             state = str(state) if len(str(state)) == 2 else "0" + str(state)

#             filename = "US-" + stateName + "-" + "census-" + naics_level_str + "-" + str(year) + ".csv"

#             curr_df = df.rename(columns={"relevant_naics":"Naics", "estab":"Establishments", "emp":"Employees", "payann":"Payroll"})

#             curr_df.to_csv(f"../../../community-data/industries/naics/US/states-update/{stateName}/{filename}", index=False)

#         d1y = d1[d1.YEAR==year]
#         d2y = d2[d2.YEAR==year]
#         d3y = d3[d3.YEAR==year]

#         d1y = d1y.drop(["YEAR"],axis=1)
#         d2y = d2y.drop(["YEAR"],axis=1)
#         d3y = d3y.drop(["YEAR"],axis=1)

#         save_state_data(state, d1y, "naics2")
#         save_state_data(state, d2y, "naics4")
#         save_state_data(state, d3y, "naics6")

# %% [markdown]
# ### statewide data from API, The correct version

# %%
state_data_dir = out_data_dir / 'state_level'
if not state_data_dir.exists():
    state_data_dir.mkdir(parents=True)

# %%
# Base URL for the API call
base_url = "https://api.census.gov/data"

#
# NOTE Years Prior to 2012 Currently have a bug when specifying NAICS#### as one of the columns
#      - stick to 2012 and later for now
#

def get_state_cbp(fips, state, years):
    count=0
    for year in years:
        print(f"Getting data for state: {state}\tyear: {year}")
        if year>=2000 and year<=2002:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS1997_TTL,ESTAB,EMP,PAYANN"
            url=f"{base_url}/{year}/cbp?get={columns_to_select}&for=state:{fips:02d}"
        elif year>=2003 and year<=2007:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2002_TTL,ESTAB,EMP,PAYANN"
            url=f"{base_url}/{year}/cbp?get={columns_to_select}&for=state:{fips:02d}"
        elif year>=2008 and year<=2011:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2007_TTL,ESTAB,EMP,PAYANN"
            url=f"{base_url}/{year}/cbp?get={columns_to_select}&for=state:{fips:02d}"
        elif year>=2012 and year<=2016:
            columns_to_select = "GEO_ID,GEO_TTL,COUNTY,YEAR,NAICS2012,NAICS2012_TTL,ESTAB,EMP,PAYANN"
            url=f"{base_url}/{year}/cbp?get={columns_to_select}&for=state:{fips:02d}"
        elif year>=2017 and year <= 2021:
            columns_to_select = "GEO_ID,NAME,COUNTY,YEAR,NAICS2017,NAICS2017_LABEL,ESTAB,EMP,PAYANN"
            url=f"{base_url}/{year}/cbp?get={columns_to_select}&for=state:{fips:02d}"
    
    
        response = r.get(url, headers=api_headers)

        with open(state_data_dir / f"industriesPerState_{str.lower(state.replace(' ', ''))}_{year}.csv",'w') as resultPath:
            for line in response.text.strip().split('\n'):
                line=line.replace('[',"").replace(']',"")
                resultPath.write(line + "\n")

        print("  > Finished CSV for year"+str(year))

# %%
for fips in state_fips.FIPS.unique():
     state = state_fips.query(f'FIPS=={fips}').values[0][0]
     years=range(startyear,endyear+1)
     get_state_cbp(fips, state, years)

# %%
df_state = pd.concat(load_all_states(state_data_dir)).drop("is5", axis=1)

# %%
df_state

# %%
df_state['fips'] = df_state.GEO_ID.apply(lambda GID: GID.split('US')[1])
df_state

# %%
df_state["COUNTY"] = 0
df_state

# %%
naics_str = "relevant_naics"
naics_ttl = "NAICS_TTL"
geo_ttl = "GEO_TTL"

newDF_state = df_state.filter(['fips', 'state', 'COUNTY', 'YEAR' ,geo_ttl, naics_str, naics_ttl,'NAICS_Sector', "estab", "emp", "payann"], axis=1)
newDF_state

# %%
df_naics_2_state = naics_level(newDF_state, 2).reset_index(drop=True)
df_naics_3_state = naics_level(newDF_state, 3).reset_index(drop=True)
df_naics_4_state = naics_level(newDF_state, 4).reset_index(drop=True)
df_naics_5_state = naics_level(newDF_state, 5).reset_index(drop=True)
df_naics_6_state = naics_level(newDF_state, 6).reset_index(drop=True)

df_naics_2_state = df_naics_2_state[df_naics_2_state.relevant_naics != '00']
df_naics_3_state = df_naics_3_state[df_naics_3_state.relevant_naics != '00']
df_naics_4_state = df_naics_4_state[df_naics_4_state.relevant_naics != '00']
df_naics_5_state = df_naics_5_state[df_naics_5_state.relevant_naics != '00']
df_naics_6_state = df_naics_6_state[df_naics_6_state.relevant_naics != '00']

# %%
df_naics_2_state

# %% [markdown]
# ### Comment & uncomment the following code block with CAUTION

# %%
#NOTE: Uncomment if you want to generate the state naics datasets using the state cbp api directly.
#NOTE: If the code blaock is uncommented, make sure that the state naics generation block (above in the nb) using county cbp api is COMMENTED.

states=newDF.state.unique()

a = df_naics_2_state
b = df_naics_4_state
c = df_naics_6_state
for state in states:
    stateName=stateFips.loc[stateFips.FIPS==state,"Postal Code"].values[0]
    print(stateName)

    a1 = a[a.state==state]
    b1 = b[b.state==state]
    c1 = c[c.state==state]

    a1 = a1.drop(["COUNTY", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state"],axis=1)
    b1 = b1.drop(["COUNTY", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state"],axis=1)
    c1 = c1.drop(["COUNTY", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state"],axis=1)


    repo_dir = pathlib.Path().cwd()
    # state_dir = repo_dir.parents[2] / 'us' / 'state-naics-update' / stateName / 'state-naics-api'
    # state_dir = repo_dir.parents[2] / 'industries' / 'naics' / 'US' / 'counties-update' / stateName / 'state-naics-api'
    state_dir = repo_dir.parents[2] / 'community-data' / 'industries' / 'naics' / 'US' / 'states-update' / stateName
    
    if not state_dir.exists():
        state_dir.mkdir(parents=True)

    for year in range(startyear, endyear+1):
        
        ay = a1[a1.YEAR==year]
        by = b1[b1.YEAR==year]
        cy = c1[c1.YEAR==year]

        ay = ay.drop(["YEAR"],axis=1)
        ay = ay.drop(["fips"],axis=1)
        by = by.drop(["YEAR"],axis=1)
        by = by.drop(["fips"],axis=1)
        cy = cy.drop(["YEAR"],axis=1)
        cy = cy.drop(["fips"],axis=1)

        def save_state_data(state, df, naics_level_str):
                
            state = str(state) if len(str(state)) == 2 else "0" + str(state)

            filename = "US-" + stateName + "-" + "census-" + naics_level_str + "-" + str(year) + ".csv"

            curr_df = df.rename(columns={"relevant_naics":"Naics", "estab":"Establishments", "emp":"Employees", "payann":"Payroll"})

            curr_df.to_csv(f"../../../community-data/industries/naics/US/states-update/{stateName}/{filename}", index=False)


        save_state_data(state, ay, "naics2")
        save_state_data(state, by, "naics4")
        save_state_data(state, cy, "naics6")

# %% [markdown]
# ### US Countrywide Naics Datatset

# %%
states=newDF.state.unique()

a = df_naics_2_state
b = df_naics_4_state
c = df_naics_6_state

for year in range(startyear, endyear+1):
    print(year)

    ay = a[a["YEAR"]==year]
    by = b[b["YEAR"]==year]
    cy = c[c["YEAR"]==year]

    ay = ay.drop(["YEAR"],axis=1)
    by = by.drop(["YEAR"],axis=1)
    cy = cy.drop(["YEAR"],axis=1)

    a1 = ay.drop(["COUNTY", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state"],axis=1)
    b1 = by.drop(["COUNTY", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state"],axis=1)
    c1 = cy.drop(["COUNTY", "GEO_TTL", "NAICS_Sector", "NAICS_TTL", "state"],axis=1)

    a1 = a1.groupby(['fips','relevant_naics'], as_index=False).sum()
    b1 = b1.groupby(['fips','relevant_naics'], as_index=False).sum()
    c1 = c1.groupby(['fips','relevant_naics'], as_index=False).sum()

    repo_dir = pathlib.Path().cwd()
    country_dir = repo_dir.parents[2] / 'community-data' / 'industries' / 'naics' / 'US' / 'country-update'

    if not country_dir.exists():
        country_dir.mkdir(parents=True)

    def save_country_data(df, naics_level_str):

        filename = "US-" + "census-" + naics_level_str + "-" + str(year) + ".csv"

        curr_df = df.rename(columns={"fips":"Fips", "relevant_naics":"Naics", "estab":"Establishments", "emp":"Employees", "payann":"Payroll"})

        curr_df.to_csv(f"../../../community-data/industries/naics/US/country-update/{filename}", index=False)

    save_country_data(a1, "naics2")
    save_country_data(b1, "naics4")
    save_country_data(c1, "naics6")
    

# %%
# NOTE: Code to remove files and directories from data_raw
# NOTE: Uncomment and run only after you have generated the datasets by running all the abaove code blocks.
# def del_data_raw(bea_data_dir):
    
#     for i in range(startyear,endyear+1):

#         x="_"+str(i)
#         files = [f for f in bea_data_dir.iterdir() if x in f.name]

#         for f in files:
#             os.remove(f)

#     os.rmdir(bea_data_dir)

# del_data_raw(county_data_dir)
# del_data_raw(state_data_dir)

# %% [markdown]
# # Zipcode Level Data

# %%
import utilities.zipcode_utility as zu

zipcodes = pd.read_csv('../../../community-data/us/zipcodes/zipcodes2.csv')

zip_data_dir = out_data_dir
if not zip_data_dir.exists():
    zip_data_dir.mkdir(parents=True)

# Default Zip path is '../../../community-data/industries/naics/US/zips'
zip_util = zu.ZipCodeUtility(api_headers=api_headers, base_path=zip_data_dir)

# %%
zip_util.get_all_zip_zbp(zipcodes)


