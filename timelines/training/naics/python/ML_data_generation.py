#!/usr/bin/env python
# coding: utf-8

# In[1]:


import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import geopandas as gpd
import requests
from io import StringIO
from geopy.geocoders import Nominatim
import os, re, sys
import numpy as np
import datetime

def get_df(url):
    try:
        response = requests.get(url)
        df = pd.read_csv(StringIO(response.text),dtype={"Fips":str})
        return df
    except:
        return pd.DataFrame()

def get_name_population_cencusdata(year,fips):
    try:
        import censusdata
        state_fips_code = fips[0:-3]
        county_fips_code= fips[-3:]
        api_key='25064f2ad0d7a1f2dfb6e603cbc4b096410bb414'
        data = pd.DataFrame(censusdata.download('acs5', year, censusdata.censusgeo([('state', state_fips_code), ('county',county_fips_code )]), ['B01003_001E'], 
                                                key=api_key))
        data=data.reset_index().rename(columns={'index': 'county',"B01003_001E":"total_population"})
        data.county=data.county.apply(lambda x: str(x).split(",")[0])
        return data.county[0],round(int(data.total_population[0])/1000)
    except:
            return '',np.nan

def get_long_lat(name):
    try:
        geolocator = Nominatim(user_agent="my_geocoder")
        county_coordinates = {}
        location = geolocator.geocode(name)
        lat=round(location.latitude,2)
        lon=round(location.longitude,2)
        return lon,lat
    except:
        return np.nan,np.nan

def get_area(test, state_fp):
    # test = gpd.read_file(f'https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_county_500k.zip')
    tost = test.copy()
    tost= tost.to_crs({'init': 'epsg:3035'})
    tost["Km2"] = round(tost['geometry'].area/ 10**6,2)
    tost=tost[tost.STATEFP==state_fp]
    tost["Fips"]=tost.STATEFP+tost.COUNTYFP
    return tost[["Fips","Km2"]]

def get_block_group_area(year, state_fp):
    block_groups = gpd.read_file(f'https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_{state_fp}_bg_500k.zip')
    block_groups_copy = block_groups.copy()
    block_groups_copy = block_groups_copy.to_crs({'init': 'epsg:3035'})
    block_groups_copy["Km2"] = block_groups_copy['geometry'].area/ 10**6
    block_groups_copy["ALAND"]=block_groups_copy.ALAND/10**6
    block_groups_copy["Fips"]= block_groups_copy.STATEFP+block_groups_copy.COUNTYFP
    return block_groups_copy[["Fips","GEOID", "Km2","ALAND"]]

def get_full_code(input_string):
    pattern = r'state:(\d+)> county:(\d+)> tract:(\d+)> block group:(\d+)'
    # Use re.search to find the match
    match = re.search(pattern, input_string)
    # Extract the codes
    state_code = match.group(1)
    county_code = match.group(2)
    tract_code = match.group(3)
    block_group_code = match.group(4)
    # Concatenate the codes
    full_code = state_code + county_code + tract_code + block_group_code
    return full_code

def get_census_block_population(year,state_fp):
    import censusdata
    api_key='25064f2ad0d7a1f2dfb6e603cbc4b096410bb414'
    data = pd.DataFrame(censusdata.download('acs5', year, censusdata.censusgeo([('state', state_fp), ('county','*'), ('block group', '*')]), ['B01003_001E'],
                                            key=api_key))
    data=data.reset_index().rename(columns={'index': 'GEOID',"B01003_001E":"total_population"})
    data.GEOID=data.GEOID.apply(lambda x: get_full_code(str(x)))
    return data

# urban density/ urban percent
def get_urban_percent(year,state_fp):
    block_gp_area = get_block_group_area(year, state_fp)
    block_gp_population = get_census_block_population(year,state_fp)
    df = block_gp_area.merge(block_gp_population, on="GEOID", how="inner")
    df["UrbanDensity"]=round(df.total_population/df.Km2,2)
    df1=df[df.UrbanDensity>1500]
    df2=pd.DataFrame(df1.groupby(["Fips"])["UrbanDensity"].mean())
    df2["UrbanDensity"] = df2["UrbanDensity"]/1000
    df2["UrbanDensity"] = df2["UrbanDensity"].round(2)
    df3=pd.DataFrame(df1.groupby(["Fips"])["ALAND"].sum())
    df4=pd.DataFrame(df.groupby(["Fips"])["ALAND"].sum())
    df4=df4.merge(df3,how="left",on="Fips")
    df4["PercentUrban"]=round(df4["ALAND_y"]/df4["ALAND_x"]*100,2)
    df4=df4[["PercentUrban"]]
    return df2,df4
    


# In[2]:


def main(year,state):
    naics_level_l=[2,4,6]
    naics_value=2
    url = f"https://model.earth/community-data/industries/naics/US/counties/{state}/US-{state}-census-naics{naics_value}-counties-{year}.csv"
    df=get_df(url)
    cencus_df=pd.DataFrame()
    cencus_df["Fips"]=df.Fips.unique()
    cencus_df["Name"]=cencus_df.Fips.apply(lambda x:get_name_population_cencusdata(year,x)[0])
    cencus_df["Population"]=cencus_df.Fips.apply(lambda x:get_name_population_cencusdata(year,x)[1])
    cencus_df['Longitude']=cencus_df.Name.apply(lambda x:get_long_lat(x)[0])
    cencus_df['Latitude']=cencus_df.Name.apply(lambda x:get_long_lat(x)[1])
    state_code=str(cencus_df.Fips[0])[0:2]
    test = gpd.read_file(f'https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_county_500k.zip')
    area_df=get_area(test, state_code)
    cencus_df=cencus_df.merge(area_df,how="left",on="Fips")
    df2,df4=get_urban_percent(year,state_code)
    cencus_df1=cencus_df.merge(df2,how="left",on="Fips")
    cencus_df2=cencus_df1.merge(df4,how="left",on="Fips")
    cencus_df2=cencus_df2.fillna(0)
    for naics_value in naics_level_l:
        url = f"https://model.earth/community-data/industries/naics/US/counties/{state}/US-{state}-census-naics{naics_value}-counties-{year}.csv"
        df=get_df(url)
        df=df.rename(columns={"Establishments":"Est","Employees":"Emp","Payroll":"Pay"})
        df=df.pivot_table(index="Fips", columns='Naics', values=["Est","Emp","Pay"]).reset_index()
        df.columns = [f"{a}-{str(b)}" for a,b in df.columns]
        sorted_columns = ["Fips-"]+sorted(df.columns[1:], key=lambda x: int(x.split('-')[-1]))
        df = df[sorted_columns].rename(columns={"Fips-":"Fips"})
        df=cencus_df2.merge(df,how="left",on="Fips")
        df1=df.copy()
        for x in df1.columns:
            if x[0:3] in ["Est","Emp","Pay"]:
                df1[x] = df1[x].astype(str).str.replace(r'\.0$', '', regex=True).replace("nan","")
        output_dir = f"output/NAICS{naics_value}/{year}"
        os.makedirs(output_dir, exist_ok=True)
        path = f"{output_dir}/US-{state}-training-naics{naics_value}-counties-{year}.csv"
        df1.to_csv(path, header=True, index=False)

if __name__=='__main__':
    sys.exit(main(int(sys.argv[1]), sys.argv[2]))
    
# In[3]:

"""
year_range=range(2017,2022)
state_list=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

for i in year_range:
    for j in state_list:
        print(f"Starting task for year{i}, state{j}...")
        try:
            main(i, j)
            print(f"Succeed. year {i}:state {j} has been saved.")
            print("=================================")
        except:
            print(f"Failed to generate output for year{i}, state{j}.")
            print("=================================")
            continue
"""

