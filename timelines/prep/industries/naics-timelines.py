# Generates year rows with NAICS columns
# Ronan 2024

import pandas as pd
import os

def construct_url(state, year):
    return f"https://model.earth/community-data/industries/naics/US/counties/{state}/US-{state}-census-naics4-counties-{year}.csv"

def aggregate_and_save_data(states, years, output_base, cells=["Establishments", "Employees", "Payroll"]):
    if not os.path.exists(output_base):
        os.makedirs(output_base)

    for state in states:
        state_output_folder = os.path.join(output_base, state)
        if not os.path.exists(state_output_folder):
            os.makedirs(state_output_folder)
            
        for cell in cells:
            data = pd.DataFrame()  

            for year in years:
                url = construct_url(state, year)
                try:
                    storage_options = {'User-Agent': 'Mozilla/5.0'}
                    df_year = pd.read_csv(url, storage_options=storage_options)

                    if cell in df_year.columns:
                        df_agg = df_year.groupby('Naics', as_index=False)[cell].sum()
                        df_agg['Naics'] = df_agg['Naics'].apply(lambda x: f"N{x}")
                        df_agg.set_index('Naics', inplace=True)
                        # Only add columns which do not include the year
                        columns_to_add = {col: f"{year}" for col in df_agg.columns if str(year) not in col}
                        df_agg.rename(columns=columns_to_add, inplace=True)
                    
                        
                        
                        data = data.join(df_agg, how='outer')

                except Exception as e:
                    print(f"An error occurred while processing {state} {year}: {e}")

            
            data = data.T  
            output_path = os.path.join(state_output_folder, f"US-{state}-census-naics4-{cell.lower()}.csv")
            data.to_csv(output_path, index_label='Year')  # Save the DataFrame to CSV
            print(f"Saved {state} {cell} data to {output_path}")

# Usage
base_dir = os.getcwd()
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

years = [2017, 2018, 2019, 2020]  
#output_base = os.path.join(base_dir, "outputs") 
output_base = "../../../../community-timelines/industries/naics4/states"

aggregate_and_save_data(states, years, output_base)

