# Generates year rows with NAICS columns
# Ronan updating initial script from Honglin

import pandas as pd
import os

base_dir = os.getcwd()
inputs_dir = os.path.join(base_dir, "inputs")
outputs_dir = os.path.join(base_dir, "outputs")
all_files = os.listdir(inputs_dir)
csv_files = [file for file in all_files if file.endswith('.csv')]
years = [int(file.split('-')[-1].split('.')[0]) for file in csv_files]
year2csv = dict(zip(years,csv_files))
print(year2csv)

cells = ["Establishments","Employees","Payroll"]
prefix = "US-AK-census-naics4-"

def output_cell_csv(year2csv, cell, prefix, inputs_dir, outputs_dir):
    years = sorted(year2csv.keys())
    df_cell = pd.DataFrame()
    df_cell["Year"] = years
    year2output = dict()
    naics_total = set()
    
    for year in years:
        csv_file = year2csv[year]
        df = pd.read_csv(os.path.join(inputs_dir, csv_file))
        naics_values = set(df["Naics"].tolist())
        naics_total.update(naics_values)
    
        year2output[year] = dict(zip(df["Naics"], df[cell]))
    
    for naics in sorted(naics_total):
        df_cell["N"+str(naics)] = [year2output[year].get(naics, None) for year in years]
    
    df_cell.to_csv(os.path.join(outputs_dir, (prefix+cell.lower()+".csv")), index=False)

for cell in cells:
    output_cell_csv(year2csv, cell, prefix, inputs_dir, outputs_dir)
    
#-----------
import pandas as pd
import os
import certifi

def construct_url(state, year):
    return f"https://model.earth/community-data/industries/naics/US/counties/{state}/US-{state}-census-naics4-counties-{year}.csv"

base_dir = os.getcwd()
outputs_dir = os.path.join(base_dir, "outputs")
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
cells = ["Establishments","Employees","Payroll"]
years = [2017,2018]
i = 0
for state in states:
    
    prefix = f"US-{state}-census-naics4-"
    for cell in cells:
        i += 1
        df_cell = pd.DataFrame()
        df_cell["Year"] = years
        naics_total = set()
        year2output = {}

        for year in years:
            url = construct_url(state, year)
            try:
                storage_options = {'User-Agent': 'Mozilla/5.0'}
                df = pd.read_csv(url, storage_options=storage_options)
    
                naics_values = set(df["Naics"].tolist())
                naics_total.update(naics_values)
                year2output[year] = dict(zip(df["Naics"], df[cell]))
            except Exception as e:
                print(f"Error reading data for {state} in year {year}: {e}")

        for naics in sorted(naics_total):
            df_cell["N"+str(naics)] = [year2output[year].get(naics, None) for year in years]
        
        output_filename = f"{prefix}{cell.lower()}.csv"
        output_path = os.path.join(outputs_dir, output_filename)
        df_cell.to_csv(output_path, index=False)