import pandas as pd
import numpy as np
import requests
import io
import os
    
def getTop4Establishment(country, stateAbbr, naicsLevel, year, state, outputFolder):
    csv_url = f"https://model.earth/community-data/industries/naics/{country}/counties/{stateAbbr}/{country}-{stateAbbr}-census-naics{str(naicsLevel)}-{str(year)}.csv"
    industry_url = "https://model.earth/community-data/us/id_lists/industry_id_list.csv"
    #df_input = pd.read_csv(csv_url)
    #df_industry = pd.read_csv(industry_url)
    df_input = pd.read_csv(io.StringIO(requests.get(csv_url).content.decode('utf-8')))
    df_industry = pd.read_csv(io.StringIO(requests.get(industry_url).content.decode('utf-8')))

    df_sorted = df_input.sort_values(by="Establishments", ascending=False)
    df_extracted = df_sorted.iloc[:4, :].reset_index(drop=True)
    #print(df_extracted)

    df_merged = pd.merge(df_extracted, df_industry, left_on='Naics', right_on='relevant_naics', how='left')
    df_merged.drop(['relevant_naics', "Unnamed: 0"], axis=1, inplace=True)
    df_merged.rename(columns={"industry_detail": "Industry"}, inplace=True)

    df_repeated = pd.DataFrame(np.repeat(df_merged.values, 4, axis=0), columns=df_merged.columns)
    df_repeated["Count"] = np.tile(np.array([1,2,3,4]), 4)
    
    df_repeated['Prompt'] = None
    
    def getPrompt(industry_list, state, year):
        assert len(industry_list) == 4
        output_list = []

        for industry in industry_list:
            prompts = [
                f"A small-honey-bee is near a location that provides {industry} in {state} in {str(year)}. Golden hour photograph. --no signage",
                f"Biking under a tree canopy near near a location that provides {industry} in {state} in {str(year)}. Golden hour photograph. --no signage",
                f"A person uses an innovation that creates jobs in {industry} in {state} in {str(year)}. Golden hour photograph. --no signage",
                f"An amazing innovation that reduces poverty in {industry} in {state} in {str(year)}. Golden hour photograph. --no signage"
            ]
            output_list.extend(prompts)
        return output_list

    df_repeated["Prompt"] = getPrompt(list(df_merged["Industry"]), state, year)
        

    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    print(df_repeated)
    
    output_name = f"{stateAbbr}-prompts-{str(year)}.csv"
    df_repeated.to_csv(os.path.join(outputFolder, output_name),index=False)
    
getTop4Establishment("US", "ME", 4, 2021, "Maine", "prompts/industries")
getTop4Establishment("US", "OR", 4, 2021, "Oregon", "prompts/industries")