import numpy as np
import pandas as pd
import requests
import os 
import json
import pandas as pd

state_info = "USEEIOv2.0.1-411"

url_Q = f"https://smmtool.app.cloud.gov/api/{state_info}/matrix/q"
url_D = f"https://smmtool.app.cloud.gov/api/{state_info}/matrix/D"
url_indicator = f"https://smmtool.app.cloud.gov/api/{state_info}/indicators"
url_sector = f"https://smmtool.app.cloud.gov/api/{state_info}/sectors" 

data_D = np.array(requests.get(url_D).json())
data_Q = np.array(requests.get(url_Q).json()).reshape(-1)
data_indicator = requests.get(url_indicator).json()
data_sector = requests.get(url_sector).json()

def get_code_index(data_indicator):
    for i in data_indicator:
        if i["code"]=="JOBS":
            return i
    return None

indicator_JOBS = get_code_index(data_indicator)
D_JOBS = data_D[indicator_JOBS["index"]]
outputs = []
for s in data_sector:
    sector_index = s["index"]
    output = {}
    output["Commodity"] = s["name"]
    output["Location"] = s["location"]
    output["TotalCommodityOutput"] = round(data_Q[sector_index])
    output["Jobs"] = round(data_Q[sector_index] * D_JOBS[sector_index])
    outputs.append(output)

pd.DataFrame(outputs).to_csv(f"{state_info}.csv",index=False)