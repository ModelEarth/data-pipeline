import numpy as np
import pandas as pd
import requests
import os 
import json
import pandas as pd

state_info = "USEEIOv2.0.1-411"

#url_Q = f"https://smmtool.app.cloud.gov/api/{state_info}/matrix/q"
url_Q = f"https://raw.githubusercontent.com/ModelEarth/io/main/build/api/{state_info}/matrix/Q.json"
#url_D = f"https://smmtool.app.cloud.gov/api/{state_info}/matrix/D"
url_D = f"https://raw.githubusercontent.com/ModelEarth/io/main/build/api/{state_info}/matrix/D.json"
#url_indicator = f"https://smmtool.app.cloud.gov/api/{state_info}/indicators"
url_indicator = f"https://raw.githubusercontent.com/ModelEarth/io/main/build/api/{state_info}/indicators.json"
#url_sector = f"https://smmtool.app.cloud.gov/api/{state_info}/sectors" 
url_sector = f"https://raw.githubusercontent.com/ModelEarth/io/main/build/api/{state_info}/sectors.json"

data_D = np.array(requests.get(url_D).json())
data_Q = np.array(requests.get(url_Q).json()).reshape(-1)
data_indicator = requests.get(url_indicator).json()
data_sector = requests.get(url_sector).json()

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
    if input >= 1e9:
        # Round to billions
        return f"{input / 1e9:.1f} Billion"
    elif input >= 1e6:
        # Round to millions
        return f"{input / 1e6:.1f} Million"
    elif input >= 1e3:
        # Round to thousands
        return f"{input / 1e3:.1f} K"
    elif input >= 100:
        # Round to one decimal
        return f"{input:.1f}"
    else:
        # Format with scientific notation with one digit after decimal
        return f"{input:.1f}"

indicator_JOBS = get_code_index(data_indicator)
D_JOBS = data_D[indicator_JOBS["index"]]
outputs = []
for s in data_sector:
    sector_index = s["index"]
    output = {}
    output["Commodity"] = s["name"]
    output["Location"] = s["location"]
    output["TotalCommodityOutput"] = format_cell(round(data_Q[sector_index]),"easy")
    output["Jobs"] = format_cell(round(data_Q[sector_index] * D_JOBS[sector_index]),"easy")
    outputs.append(output)

pd.DataFrame(outputs).to_csv(f"{state_info}.csv",index=False)