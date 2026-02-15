# Now resides as data-pipeline/timelines/prep/industries/naics-timelines.py

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