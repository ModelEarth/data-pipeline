#!/usr/bin/env python
# coding: utf-8

# In[1]:
import numpy as np
import pandas as pd
import requests
import os 
import json
import pandas as pd

def get_code_index(data_indicator):
    for i in data_indicator:
        if i["code"]=="JOBS":
            return i
    return None

def format_cell(input, format):
    # If format is none or blank, return input as it is
    if format == 'none' or format == '':
        return input

    # Format as scientific notation
    if format == 'scientific':
        return f"{input:.1f}"

    # Format as easy
    if input >= 1e12:
        # Round to billions
        input1=str(round(input / 1e12,1))
        # input1=input1.replace('.0', '')
        return input1+' Trillion'
    elif input >= 1e9:
        # Round to billions
        input1=str(round(input / 1e9,1))
        # input1=input1.replace('.0', '')
        return input1+' Billion'
    elif input >= 1e6:
        # Round to millions
        #return f"{input / 1e6:.1f} Million"
        input1=str(round(input / 1e6,1))
        input1=input1.replace('.0', '')
        return input1+' Million'
    elif input >= 1e3:
        # Round to thousands
        #return f"{input / 1e3:.1f} K"
        input1=str(round(input / 1e3,1))
        input1=input1.replace('.0', '')
        return input1+' K'
    elif input >= 100:
        # Round to one decimal
        return f"{input}"
    else:
        # Format with scientific notation with one digit after decimal
        return f"{input:.1f}"


# In[2]:
state_list=['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
all_states_info=[state+'EEIOv1.0-s-20' for state in state_list]
all_states_info.append('USEEIOv2.0.1-411')


# In[3]:
output_dir = f"states/commodities/2020"
os.makedirs(output_dir, exist_ok=True)

# In[4]:
for state_info in all_states_info:
    url_Q = f"https://raw.githubusercontent.com/ModelEarth/OpenFootprint/main/impacts/2020/{state_info}/matrix/q.json"
    url_D = f"https://raw.githubusercontent.com/ModelEarth/OpenFootprint/main/impacts/2020/{state_info}/matrix/D.json"
    url_indicator = f"https://raw.githubusercontent.com/ModelEarth/OpenFootprint/main/impacts/2020/{state_info}/indicators.json"
    url_sector = f"https://raw.githubusercontent.com/ModelEarth/OpenFootprint/main/impacts/2020/{state_info}/sectors.json"

    data_D = np.array(requests.get(url_D).json())
    data_Q = np.array(requests.get(url_Q).json()).reshape(-1)
    data_indicator = requests.get(url_indicator).json()
    data_sector = requests.get(url_sector).json()

    indicator_JOBS = get_code_index(data_indicator)
    D_JOBS = data_D[indicator_JOBS["index"]]
    outputs = []
    for s in data_sector:
        sector_index = s["index"]
        output = {}
        output["Commodity"] = s["name"]
        output["Location"] = s["location"]
        output["Commodities"]=round(data_Q[sector_index])
        output["Employees"]=round(data_Q[sector_index] * D_JOBS[sector_index])
        output["Output"] = format_cell(output["Commodities"],"easy") # Raw_output
        output["Jobs"] = format_cell(output["Employees"],"easy") # Raw Jobs
        outputs.append(output)
    
    df=pd.DataFrame(outputs)
    df=df.sort_values(by=["Commodities"],ascending=False)

    df=df[["Commodity","Location","Commodities","Output","Employees","Jobs"]]
    df.to_csv(f"{output_dir}/{state_info}.csv",index=False)




