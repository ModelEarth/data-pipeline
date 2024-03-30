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

all_states_info = ["AKEEIOv1.0-s-20","ALEEIOv1.0-s-20","AREEIOv1.0-s-20","AZEEIOv1.0-s-20","CAEEIOv1.0-s-20","COEEIOv1.0-s-20","CTEEIOv1.0-s-20","DEEEIOv1.0-s-20","FLEEIOv1.0-s-20","GAEEIOv1.0-s-20","HIEEIOv1.0-s-20","IAEEIOv1.0-s-20","IDEEIOv1.0-s-20","ILEEIOv1.0-s-20","INEEIOv1.0-s-20","KSEEIOv1.0-s-20","KYEEIOv1.0-s-20","LAEEIOv1.0-s-20","MAEEIOv1.0-s-20","MDEEIOv1.0-s-20","MEEEIOv1.0-s-20","MIEEIOv1.0-s-20","MNEEIOv1.0-s-20","MOEEIOv1.0-s-20","MSEEIOv1.0-s-20","MTEEIOv1.0-s-20","NCEEIOv1.0-s-20","NDEEIOv1.0-s-20","NEEEIOv1.0-s-20","NHEEIOv1.0-s-20","NJEEIOv1.0-s-20","NMEEIOv1.0-s-20","NVEEIOv1.0-s-20","NYEEIOv1.0-s-20","OHEEIOv1.0-s-20","OKEEIOv1.0-s-20","OREEIOv1.0-s-20","PAEEIOv1.0-s-20","RIEEIOv1.0-s-20","SCEEIOv1.0-s-20","SDEEIOv1.0-s-20","TNEEIOv1.0-s-20","TXEEIOv1.0-s-20","UTEEIOv1.0-s-20","VAEEIOv1.0-s-20","VTEEIOv1.0-s-20","WAEEIOv1.0-s-20","WIEEIOv1.0-s-20","WVEEIOv1.0-s-20","WYEEIOv1.0-s-20"]

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
        output["Output"] = format_cell(round(data_Q[sector_index]),"easy")
        output["Jobs"] = format_cell(round(data_Q[sector_index] * D_JOBS[sector_index]),"easy")
        outputs.append(output)

    pd.DataFrame(outputs).to_csv(f"states/commodities/2020/{state_info}.csv",index=False)