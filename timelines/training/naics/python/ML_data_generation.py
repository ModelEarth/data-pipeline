import pandas as pd
import geopandas as gpd
import requests
from io import StringIO
from geopy.geocoders import Nominatim
import os, re, sys
import numpy as np

def get_df(url):
    try:
        response = requests.get(url)
        df = pd.read_csv(StringIO(response.text))
        return df
    except:
        return np.nan

def get_name_population_cencusdata(year,fips):
    try:
        import censusdata
        state_fips_code = str(fips)[0:-3]
        county_fips_code= str(fips)[-3:]
        data = pd.DataFrame(censusdata.download('acs5', year, censusdata.censusgeo([('state', state_fips_code), ('county',county_fips_code )]), ['B01003_001E']))
        data=data.reset_index().rename(columns={'index': 'county',"B01003_001E":"total_population"})
        data.county=data.county.apply(lambda x: str(x).split(",")[0])
        return data.county[0],data.total_population[0]
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

def get_area(year, state_fp):
    test = gpd.read_file(f'https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_county_500k.zip')
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
    block_groups_copy["Km2"] = round(block_groups_copy['geometry'].area/ 10**6,2)
    block_groups_copy["Fips"]= block_groups_copy.STATEFP+block_groups_copy.COUNTYFP
    return block_groups_copy[["Fips","GEOID", "Km2"]]

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
    data = pd.DataFrame(censusdata.download('acs5', year, censusdata.censusgeo([('state', state_fp), ('county','*'), ('block group', '*')]), ['B01003_001E']))
    data=data.reset_index().rename(columns={'index': 'GEOID',"B01003_001E":"total_population"})
    data.GEOID=data.GEOID.apply(lambda x: get_full_code(str(x)))
    return data

def get_urban_percent(year,state_fp):
    block_gp_area = get_block_group_area(year, state_fp)
    block_gp_population = get_census_block_population(year,state_fp)
    df = block_gp_area.merge(block_gp_population, on="GEOID", how="inner")
    df_result = pd.DataFrame(round(df[df["total_population"] >= 1500].groupby("Fips")["Km2"].sum()/df.groupby("Fips")["Km2"].sum(),2))
    df_result = df_result.reset_index().rename(columns={'index': 'Fips',"Km2":"UrbanPercent"})
    return df_result


# # main funct
def main(year,state,naics_value):
    url = f"https://model.earth/community-data/industries/naics/US/counties/{state}/US-{state}-census-naics{naics_value}-counties-{year}.csv"
    df=get_df(url)
    df=df.pivot_table(index="Fips", columns='Naics', values=["Establishments","Employees","Payroll"]).reset_index()
    df.columns = [f"{a}-{str(b)}" for a,b in df.columns]
    sorted_columns = ["Fips-"]+sorted(df.columns[1:], key=lambda x: int(x.split('-')[-1]))
    df = df[sorted_columns].rename(columns={"Fips-":"Fips"})
    df.insert(loc=1, column='Name', value=df.Fips.apply(lambda x:get_name_population_cencusdata(year,x)[0]))
    df.insert(loc=2, column='Population', value=df.Fips.apply(lambda x:get_name_population_cencusdata(year,x)[1]))
    df.insert(loc=3, column='Longitude', value=df.Name.apply(lambda x:get_long_lat(x)[0]))
    df.insert(loc=4, column='Latitude', value=df.Name.apply(lambda x:get_long_lat(x)[1]))
    state_code=str(df.Fips[0])[0:2]
    area_df=get_area(year,state_code)
    df.Fips=df.Fips.astype(str)
    df=df.merge(area_df,how="left",on="Fips")
    column_data = df.pop('Km2')
    df.insert(loc=5, column='Km2', value=column_data)
    df.insert(loc=6, column='UrbanDensity', value=df.apply(lambda x:round(x.Population/x.Km2,2),axis=1))
    urban_df=get_urban_percent(year,state_code)
    df=df.merge(urban_df,how="left",on="Fips")
    column_data = df.pop('UrbanPercent')
    df.insert(loc=7, column='UrbanPercent', value=column_data)
    print(df)
    output_dir = f"../output/{year}"
    os.makedirs(output_dir, exist_ok=True)
    path = f"{output_dir}/US-{state}-training-naics{naics_value}-counties-{year}.csv"
    df.to_csv(path, header=True, index=False)

if __name__=='__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]), sys.argv[3])

"""
year_range=range(2017,2022)
state_list=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
for k in [2,4]:
  for i in year_range:
    for j in state_list:
          try:
              main(i,j,k)
              print(f"naics{k}:{i}:{j} has been saved")
          except:
              continue
"""